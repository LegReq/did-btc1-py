
from .did import encode_identifier, KEY, EXTERNAL, NETWORKS, VERSIONS
import jcs
from buidl.helper import sha256
from pydid.doc import DIDDocument
from bitcoinrpc import BitcoinRPC
from .did import PLACEHOLDER_DID
from .diddoc.doc import IntermediateBtc1DIDDocument
from .diddoc.builder import Btc1DIDDocumentBuilder
from .diddoc.updater import Btc1DIDDocumentUpdater
from buidl.tx import Tx, TxIn, TxOut, SIGHASH_DEFAULT
from buidl.script import ScriptPubKey, address_to_script_pubkey
from buidl.ecc import PrivateKey
import json
from .beacon_manager import BeaconManager

class DIDManager():

    def __init__(self, network, rpc_endpoint, rpcuser, rpcpassword):
        self.bitcoinrpc = BitcoinRPC.from_config(rpc_endpoint, (rpcuser, rpcpassword))
        self.pending_updates = []
        self.initial_document = None
        self.beacon_managers = {}
        self.did = None
        self.network = network


    async def create_deterministic(self, initial_sk, network="bitcoin", version=1):
        if network not in NETWORKS:
            raise Exception(f"Invalid Network : {network}")
        
        if network != self.network:
            raise Exception("Manager for different network")

        if version not in VERSIONS:
            raise Exception(f"Invalid Version : {version}")
        
        public_key = initial_sk.point

        builder = Btc1DIDDocumentBuilder.from_secp256k1_key(public_key, network, version)

        did_document = builder.build()

        for beacon in did_document.service:
            if "P2PKH" in beacon.id.fragment:
                script_pubkey = public_key.p2pkh_script()
                bm = BeaconManager(self.bitcoinrpc, self.network, beacon.id, initial_sk, script_pubkey)
                self.beacon_managers[beacon.id] = bm
                if network == "regtest":
                    await bm.fund_beacon_address()
            elif "P2WPKH" in beacon.id.fragment:
                script_pubkey = public_key.p2wpkh_script()
                bm = BeaconManager(self.bitcoinrpc, self.network, beacon.id, initial_sk, script_pubkey)
                self.beacon_managers[beacon.id] = bm
                if network == "regtest":
                    await bm.fund_beacon_address()
            elif "P2TR" in beacon.id.fragment:
                script_pubkey = public_key.p2tr_script()
                bm = BeaconManager(self.bitcoinrpc, self.network, beacon.id, initial_sk, script_pubkey)
                self.beacon_managers[beacon.id] = bm
                if network == "regtest":
                    await bm.fund_beacon_address()

        self.did = did_document.id
        self.document = did_document
        self.version = 1
        self.signals_metadata = {}

        return did_document.id, did_document

    def create_external(self, intermediate_document: IntermediateBtc1DIDDocument, network = "bitcoin", version = 1):
        if network not in NETWORKS:
            raise Exception(f"Invalid Network : {network}")
        
        if network != self.network:
            raise Exception("Manager for different network")

        if version not in VERSIONS:
            raise Exception(f"Invalid Version : {version}")
        
        if intermediate_document.id != PLACEHOLDER_DID:
            raise Exception(f"Intermediate Document must use placeholder id : {intermediate_document.id}")
        
        genesis_bytes = sha256(jcs.canonicalize(intermediate_document.serialize()))

        identifier = encode_identifier(EXTERNAL, version, network, genesis_bytes)

        did_document = intermediate_document.to_did_document(identifier)
        
        print(json.dumps(did_document.serialize(), indent=2))

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

        # beacon_address = beacon_address.replace("bitcoin:", "")

        ## TODO: Need to know the availabel UTXOs that can be spend for a particular beacon
        # signing_res = await self.bitcoinrpc.acall("send", {"outputs": { beacon_address: 0.2}})

        # funding_txid = signing_res["txid"]

        # funding_tx_hex = await self.bitcoinrpc.acall("getrawtransaction", {"txid": funding_txid})
        # funding_tx = Tx.parse_hex(funding_tx_hex)
        # print("Funding Tx", funding_tx)
        # for index, tx_out in enumerate(funding_tx.tx_outs):
        #     if beacon_address == tx_out.script_pubkey.address(network=self.network):
        #         prev_index = index
        #         break
        #     # print("TXOUT", )
        # prev_tx = bytes.fromhex(funding_txid)  # Identifying funding tx

        # tx_in = TxIn(prev_tx=prev_tx, prev_index=prev_index)
        # tx_in._script_pubkey = funding_tx.tx_outs[prev_index].script_pubkey
        # tx_in._value = funding_tx.tx_outs[prev_index].amount
            
        update_hash = sha256(jcs.canonicalize(secured_update))

        pending_beacon_signal = beacon_manager.construct_beacon_signal(update_hash)

        signed_tx = beacon_manager.sign_beacon_signal(pending_beacon_signal)

        signal_id = await self.bitcoinrpc.acall("sendrawtransaction", {"hexstring": signed_tx.serialize().hex()})

        # script_pubkey = ScriptPubKey([0x6a, update_hash])

        # beacon_signal_txout = TxOut(0, script_pubkey)

        # tx_fee = 350

        # refund_amount = tx_in.value() - tx_fee

        
        # refund_script_pubkey = beacon_sk.point.p2wpkh_script()
        # refund_out = TxOut(amount=refund_amount, script_pubkey=refund_script_pubkey)
        # tx_ins = [tx_in]

        # tx_outs = [beacon_signal_txout, refund_out]
        # pending_beacon_signal = Tx(version=1, tx_ins=tx_ins, tx_outs=tx_outs, network=self.network,segwit=True)

        # signing_res = pending_beacon_signal.sign_input(0, beacon_sk)
        # print(signing_res)
        # if not signing_res:
        #     raise Exception("Invalid Beacon Key, unable to sign signal")
        
        # signed_hex = pending_beacon_signal.serialize().hex()
        # signal_id = await self.bitcoinrpc.acall("sendrawtransaction", {"hexstring": signed_hex})
        
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




    def get_sidecar_data(self):
        sidecarData = {
            "did": self.did,
        }

        if self.initial_document:
            sidecarData["initialDocument"] = self.initial_document.serialize()

        if self.signals_metadata:
            sidecarData["signalsMetadata"] = self.signals_metadata

        return sidecarData
    
