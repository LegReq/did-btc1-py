
from .did import encode_identifier, KEY, EXTERNAL, NETWORKS, VERSIONS
import jcs
from buidl.helper import sha256
from pydid.doc import DIDDocument
from .did import PLACEHOLDER_DID
from .diddoc.doc import IntermediateBtc1DIDDocument, Btc1Document
from .diddoc.builder import Btc1DIDDocumentBuilder
from .diddoc.updater import Btc1DIDDocumentUpdater
from buidl.tx import Tx, TxIn, TxOut, SIGHASH_DEFAULT
from buidl.script import ScriptPubKey, address_to_script_pubkey
from buidl.ecc import PrivateKey
import json
from .beacon_manager import BeaconManager
from .esplora_client import EsploraClient
from .resolver import Btc1Resolver



class DIDManager():

    def __init__(self, did_network, btc_network = None, esplora_base="http://localhost:3000"):
        
        self.esplora_client = EsploraClient(esplora_base)
        self.pending_updates = []
        self.initial_document = None
        self.beacon_managers = {}
        self.did = None
        self.did_network = did_network
        self.btc_network = btc_network if btc_network is not None else did_network


    async def create_deterministic(self, initial_sk, network="bitcoin", identifierVersion=1):
        if network not in NETWORKS:
            raise Exception(f"Invalid Network : {network}")
        
        if network != self.did_network:
            raise Exception("Manager for different network")

        if identifierVersion not in VERSIONS:
            raise Exception(f"Invalid Version : {identifierVersion}")
        
        public_key = initial_sk.point

        builder = Btc1DIDDocumentBuilder.from_secp256k1_key(public_key, network, identifierVersion)

        did_document = builder.build()

        for beacon in did_document.beacon_services():
            if "P2PKH" in beacon.id.fragment:
                script_pubkey = public_key.p2pkh_script()
                self.add_beacon_manager(beacon.id, initial_sk, script_pubkey)
            elif "P2WPKH" in beacon.id.fragment:
                self.add_beacon_manager(beacon.id, initial_sk, public_key.p2wpkh_script())
            elif "P2TR" in beacon.id.fragment:
                self.add_beacon_manager(beacon.id, initial_sk, public_key.p2tr_script())


        self.did = did_document.id
        self.document = did_document
        self.version = 1
        self.signals_metadata = {}

        return did_document.id, did_document

    def create_external(self, intermediate_document: IntermediateBtc1DIDDocument, network = "bitcoin", version = 1):
        if network not in NETWORKS:
            raise Exception(f"Invalid Network : {network}")
        
        if network != self.did_network:
            raise Exception("Manager for different network")

        if version not in VERSIONS:
            raise Exception(f"Invalid Version : {version}")
        
        if intermediate_document.id != PLACEHOLDER_DID:
            raise Exception(f"Intermediate Document must use placeholder id : {intermediate_document.id}")
        
        genesis_bytes = sha256(jcs.canonicalize(intermediate_document.serialize()))

        identifier = encode_identifier(EXTERNAL, version, network, genesis_bytes)

        did_document = intermediate_document.to_did_document(identifier)
        
        self.did = did_document.id
        self.version = 1
        self.initial_document = did_document.model_copy(deep=True)
        self.document = did_document
        self.signals_metadata = {}

        return identifier, did_document
    

    def updater(self):
        builder = Btc1DIDDocumentBuilder.from_doc(self.document.model_copy(deep=True))
        print(json.dumps(self.document.serialize(), indent=2))
        updater = Btc1DIDDocumentUpdater(builder, self.version)
        return updater
    
    async def announce_update(self, beacon_id, secured_update):
        beacon_manager = self.beacon_managers.get(beacon_id)
        # print(beacon_id)
        # for service in self.document.service:
        #     print(service)
        #     if service.id == beacon_id:
        #         beacon_service = service
        #         break

        if not beacon_manager:
            raise Exception("InvalidBeacon")
        
        # beacon_address = beacon_service.serialize()["serviceEndpoint"]

        # print("Beaocn Address", beacon_address)

        update_hash = sha256(jcs.canonicalize(secured_update))

        pending_beacon_signal = beacon_manager.construct_beacon_signal(update_hash)

        signed_tx = beacon_manager.sign_beacon_signal(pending_beacon_signal)

        signal_id = self.esplora_client.broadcast_tx(signed_tx.serialize().hex())

        self.signals_metadata[signal_id] = {
            "updatePayload": secured_update
        }

        return signal_id

    async def finalize_update_payload(self, updater, vm_id, signing_key, beacon_id):
        updater.construct_update_payload()
        secured_update = updater.finalize_update_payload(vm_id, signing_key)
        self.document = updater.builder.build()
        self.version += 1
        result = await self.announce_update(beacon_id, secured_update)
        
        if not result:
            raise Exception("Error announcing")
        return self.document

    def add_beacon_manager(self, beacon_id, initial_sk, script_pubkey):
        if beacon_id in self.beacon_managers:
            raise Exception("Beacon already exists")
        
        bm = BeaconManager(self.btc_network, beacon_id, initial_sk, script_pubkey, self.esplora_client)
        self.beacon_managers[beacon_id] = bm
        return bm


    def get_sidecar_data(self):
        sidecarData = {
            "did": self.did,
        }

        if self.initial_document:
            sidecarData["initialDocument"] = self.initial_document.serialize()

        if self.signals_metadata:
            sidecarData["signalsMetadata"] = self.signals_metadata

        return sidecarData
    

    def serialize(self):
        did_manager_data = {
            "did": self.did,
            "document": self.document.serialize(),
            "version": self.version,
            "sidecarData": self.get_sidecar_data()
        }

        return did_manager_data
    
    

    @classmethod
    def from_did(cls, did_data, did_network, btc_network, keystore, esplora_base="http://localhost:3000"):

        did = did_data["did"]
        sidecar_data = did_data["sidecarData"]
        signals_metadata = sidecar_data.get("signalsMetadata", {})
        initial_document = sidecar_data.get("initialDocument", None)
        document = did_data["document"]
        version = did_data["version"]

        did_manager = cls(did_network, btc_network, esplora_base)

        did_manager.did = did
        did_manager.document = Btc1Document.deserialize(document)

        did_manager.version = version
        did_manager.signals_metadata = signals_metadata
        did_manager.initial_document = initial_document


        for beacon in did_manager.document.beacon_services():
            beacon_sk = keystore.get_key(beacon.id)
            if not beacon_sk:
                raise Exception("Beacon key not found")
            
            address = beacon.address()
            script_pubkey = address_to_script_pubkey(address, btc_network)
            did_manager.add_beacon_manager(beacon.id, beacon_sk, script_pubkey)             

        return did_manager