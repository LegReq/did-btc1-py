from buidl.ecc import S256Point
from buidl.tx import Tx
from buidl.helper import sha256, bytes_to_str
import base58
import jcs
import os
import json
import copy
from bitcoinrpc import BitcoinRPC
from ipfs_cid import cid_sha256_wrap_digest
import urllib
import jsonpatch
from pydid.doc import DIDDocument
from pydid.doc.builder import VerificationMethodBuilder
from pydid.verification_method import Multikey
from di_bip340.cryptosuite import Bip340JcsCryptoSuite
from di_bip340.data_integrity_proof import DataIntegrityProof
from di_bip340.multikey import SchnorrSecp256k1Multikey
from .bech32 import decode_bech32_identifier
from .verificationMethod import get_verification_method
from .did import decode_identifier, KEY, EXTERNAL, InvalidDidError
from .diddoc.builder import Btc1DIDDocumentBuilder, IntermediateBtc1DIDDocumentBuilder
from .diddoc.doc import Btc1Document, IntermediateBtc1DIDDocument
from .helper import canonicalize_and_hash
from .service import BeaconTypeNames, SingletonBeaconService
CONTEXT = ["https://www.w3.org/ns/did/v1", "https://did-btc1/TBD/context"]


GENESIS_COINBASE = "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
COINBASE_TXIDS = [GENESIS_COINBASE, "0000000000000000000000000000000000000000000000000000000000000000"]

SINGLETON_BEACON_TYPE = "SingletonBeacon"
P2PKH = "p2pkh"
P2WPKH = "p2wpkh"
P2TR = "p2tr"


class Btc1Resolver():
    
    def __init__(self, rpc_endpoint, rpcuser, rpcpassword, logging=False, log_folder="TestVectors"):
        self.bitcoinrpc = BitcoinRPC.from_config(rpc_endpoint, (rpcuser, rpcpassword))
        self.logging = logging
        self.log_folder = f"{os.getcwd()}/{log_folder}"



    async def resolve(self, identifier, resolution_options=None):
    
        if self.logging == True:
            did_path = identifier.split(":")[2]
            self.log_folder = f"{self.log_folder}/{did_path}"
            if not os.path.exists(self.log_folder):
                os.makedirs(self.log_folder)

        id_type, version, network, genesis_bytes = decode_identifier(identifier)

        print("ID Components", id_type, version, network, genesis_bytes.hex())
        blockchain_info = await self.bitcoinrpc.getblockchaininfo()
        chain = blockchain_info["chain"]
        if chain != network:
            raise Exception(f"RPC connected to incorrect chain {chain}")

        if id_type == KEY:
            initial_did_document = self.resolve_deterministic(identifier, 
                                                        genesis_bytes, 
                                                        version, 
                                                        network)
        elif id_type == EXTERNAL:
            initial_did_document = await self.resolve_external(identifier, genesis_bytes, version, network, resolution_options)

        else:
            raise Exception("Invalid HRP")
        
        # TODO: Process Beacon Signals
        print("Initial DID document")
        print(json.dumps(initial_did_document.serialize(), indent=2))
        target_document = await self.resolve_target_document(initial_did_document, resolution_options, network)
        return target_document



    def resolve_deterministic(self, btc1_identifier, key_bytes, version, network):

        pubkey = S256Point.parse_sec(key_bytes)

        builder = Btc1DIDDocumentBuilder.from_secp256k1_key(pubkey, network, version)

        did_document = builder.build()

        if btc1_identifier != did_document.id:
            raise InvalidDidError("identifier does not match, deterministic document id")

        return did_document
    
    async def resolve_external(self, btc1_identifier, genesis_bytes, version, network, resolution_options):
        sidecar_data = resolution_options.get("sidecarData")
        initial_document = None
        if sidecar_data:
            doc_json = sidecar_data.get("initialDocument")
            print("Sidecar Initial External Resolve")
            print(json.dumps(doc_json, indent=2))
            initial_document = Btc1Document.deserialize(doc_json)
            
        
        if initial_document:
            initial_document = self.sidecar_initial_document_validation(btc1_identifier, genesis_bytes, version, network, initial_document)
        else:
            initial_document = self.cas_retrieval(btc1_identifier, genesis_bytes, version, network)

        # TODO: validate initial document

        return initial_document

    def sidecar_initial_document_validation(self, btc1_identifier, genesis_bytes, version, network, initial_document):
        print("Initial Doc ")
        print(json.dumps(initial_document.serialize(), indent=2))    
        intermediate_doc = IntermediateBtc1DIDDocument.from_did_document(initial_document)
        
        print("Intermediate Doc ")
        print(json.dumps(intermediate_doc.serialize(), indent=2))
        print("Initial Doc ")
        print(json.dumps(initial_document.serialize(), indent=2))        
        hash_bytes = intermediate_doc.canonicalize()
        
        if hash_bytes != genesis_bytes:
            raise InvalidDidError("Initial document provided, does not match identifier genesis bytes")

        return initial_document
    
    async def cas_retrieval(self, btc1_identifier, genesis_bytes, version, network):
        cid = cid_sha256_wrap_digest(genesis_bytes)
        # TODO: Attempt to fetch content for CID from IPFS
        raise NotImplemented

    async def resolve_target_document(self, initial_document: DIDDocument, resolution_options, network):
        request_version_id = resolution_options.get("versionId")
        versionTime = resolution_options.get("versionTime")

        if request_version_id and versionTime:
            raise Exception("InvalidResolutionOptions - cannot have versionTime and targetTime")

        if not request_version_id:
            target_blockheight = await self.determine_target_blockheight(versionTime) 

        sidecar_data = resolution_options.get("sidecarData")

        signals_metadata = None
        if sidecar_data:
            signals_metadata = sidecar_data.get("signalsMetadata")

        current_version_id = 1

        if current_version_id == request_version_id:
            return initial_document
        
        update_hash_history = []

        contemporary_blockheight = 0

        contemporary_document = initial_document.model_copy()

        target_document = await self.traverse_blockchain_history(contemporary_document, 
                                                           contemporary_blockheight, 
                                                           current_version_id, 
                                                           request_version_id, 
                                                           target_blockheight, 
                                                           update_hash_history, 
                                                           signals_metadata, 
                                                           network)

        return target_document

    # TODO: Remove
    async def determine_target_blockheight(self, versionTime):
        if versionTime:
            raise NotImplemented
        
        required_confirmations = 6

        best_blockhash = await self.bitcoinrpc.acall("getbestblockhash", {})
        bestblock = await self.bitcoinrpc.acall("getblock", {"blockhash": best_blockhash})

        confirmations = bestblock["confirmations"]
        bestblock_height = bestblock["height"]
        target_blockheight = bestblock_height + (confirmations - required_confirmations)

        return target_blockheight
    

    async def traverse_blockchain_history(self, 
                                          contemporary_document: Btc1Document, 
                                          contemporary_blockheight, 
                                          current_version_id, 
                                          request_version_id, 
                                          target_blockheight, 
                                          update_hash_history, 
                                          signals_metadata,
                                          network):
        contemporary_hash = contemporary_document.model_copy(deep=True).canonicalize()    
        beacons = []
        for service in contemporary_document.service:
            # print("SERVICETYPE", service.type, type(service))
            if service.type in BeaconTypeNames:
                beacons.append(service)

        next_signals = await self.find_next_signals(beacons, contemporary_blockheight, target_blockheight, network)


                
        

        contemporary_blockheight = next_signals["blockheight"]
        print(contemporary_blockheight, target_blockheight)
        signals = next_signals["signals"]

        updates = self.process_beacon_signals(signals, signals_metadata)
        
        if self.logging and len(updates) != 0:
            block_folder = f"{self.log_folder}/block{contemporary_blockheight}"
            if not os.path.exists(block_folder):
                os.makedirs(block_folder)
            # next_signals_path = f"{block_folder}/next_signals.json"
            
            # with open(next_signals_path, "w") as f:
            #     print(next_signals)
            #     serialized_signals = copy.deepcopy(next_signals)
            #     for index, tx in enumerate(serialized_signals["signals"]):
            #         serialized_signals["signals"][index] = tx.serialize().hex()
            #     json.dump(serialized_signals, f, indent=2)
            
            
            updates_path = f"{block_folder}/updates.json"
            
            with open(updates_path, "w") as f:
                json.dump(updates, f, indent=2)

        updates.sort(key=lambda update: update["targetVersionId"])

        for update in updates:
            target_version_id = update["targetVersionId"]
            if target_version_id <= current_version_id:
                self.confirm_duplicate_update(update, update_hash_history)
            elif target_version_id == current_version_id + 1:
                print(update["sourceHash"], bytes_to_str(base58.b58encode(contemporary_hash)))
                if update["sourceHash"] != bytes_to_str(base58.b58encode(contemporary_hash)):
                    raise Exception("Late Publishing")
                print("Apply DID Update", update)
                contemporary_document = self.apply_did_update(contemporary_document, update).model_copy(deep=True)
                if self.logging:
                    contemporary_path = f"{block_folder}/contemporaryDidDocument.json"
                    with open(contemporary_path, "w") as f:
                        json.dump(contemporary_document.serialize(), f, indent=2)
                        
                current_version_id += 1
                updateHash = sha256(jcs.canonicalize(update))
                update_hash_history.append(updateHash)
                contemporary_hash = bytes_to_str(base58.b58encode(contemporary_document.canonicalize()))
                if current_version_id == request_version_id:
                    print("Found document for target version", contemporary_document)
                    return contemporary_document

            elif target_version_id > current_version_id + 1:
                print(target_version_id, current_version_id)
                raise Exception(f"Late publishing {target_version_id} {current_version_id}") 
        
        print("Tracking", contemporary_blockheight, target_blockheight)
        if contemporary_blockheight == target_blockheight:
            print("Got to target", contemporary_blockheight)
            return contemporary_document
        
        contemporary_blockheight += 1

        target_document = await self.traverse_blockchain_history(contemporary_document,
                                                            contemporary_blockheight,
                                                            current_version_id,
                                                            request_version_id,
                                                            target_blockheight,
                                                            update_hash_history,
                                                            signals_metadata,
                                                            network)

        return target_document

    async def find_next_signals(self, beacons, contemporary_blockheight, target_blockheight, network):
        signals = []
        block_hash = await self.bitcoinrpc.getblockhash(contemporary_blockheight)
        block = await self.bitcoinrpc.getblock(block_hash)
        # print("CHecking block ", contemporary_blockheight)
        for txid in block["tx"]:
            if txid not in COINBASE_TXIDS:
                tx_hex = await self.bitcoinrpc.getrawtransaction(txid, verbose=False)
                tx = Tx.parse_hex(tx_hex)

                for tx_in in tx.tx_ins:
                    prev_txid = tx_in.prev_tx.hex()
                    if prev_txid not in COINBASE_TXIDS:
                        prev_tx_hex = await self.bitcoinrpc.getrawtransaction(prev_txid, verbose=False)
                        prev_tx = Tx.parse_hex(prev_tx_hex)

                        spent_tx_output = prev_tx.tx_outs[tx_in.prev_index]
                        spent_tx_output_address = spent_tx_output.script_pubkey.address(network="regtest")

                        beacon_signal = None
                        for beacon in beacons:
                            if beacon.address() == spent_tx_output_address:
                                beacon_signal = {
                                    "beaconId": beacon.id,
                                    "beaconType": beacon.type,
                                    "tx": tx
                                }
                                signals.append(beacon_signal)
                                print("Found Beacon Signal", tx)
                                # break
                        
                        # if beacon_signal:
                        #     break

        if contemporary_blockheight == target_blockheight:
            next_signals = {
                "blockheight": contemporary_blockheight,
                "signals": signals
            }
            return next_signals
        
        if len(signals) == 0:
            next_signals = await self.find_next_signals(beacons, contemporary_blockheight+1, target_blockheight, network)
        else:
            next_signals = {
                "blockheight": contemporary_blockheight,
                "signals": signals
            }

        return next_signals
    

    def process_beacon_signals(self, signals, signals_metadata):
        updates = []

        for signal in signals:
            type = signal["beaconType"]
            signal_tx = signal["tx"]
            signal_id = signal_tx.id()
            signal_sidecar_data = signals_metadata.get(signal_id)
            did_update_payload = None
            if type == "SingletonBeacon":
                did_update_payload = self.process_singleton_beacon_signal(signal_tx, signal_sidecar_data)

            if did_update_payload:
                updates.append(did_update_payload)
        
        return updates

    def process_singleton_beacon_signal(self, tx: Tx, signal_sidecar_data):
        tx_out = tx.tx_outs[0]
        did_update_payload = None

        if (tx_out.script_pubkey.commands[0] != 106 and len(tx_out.script_pubkey.commands[1]) != 32):
            print("Not a beacon signal")
            return did_update_payload
        
        hash_bytes = tx_out.script_pubkey.commands[1]

        if signal_sidecar_data:
            did_update_payload = signal_sidecar_data.get("updatePayload")

            if not did_update_payload:
                raise Exception("InvalidSidecarData")
            
            update_hash_bytes = sha256(jcs.canonicalize(did_update_payload))

            if update_hash_bytes != hash_bytes:
                raise Exception("InvalidSidecarData")
            
            return did_update_payload
        else:
            payload_cid = cid_sha256_wrap_digest(hash_bytes)
            # TODO: Fetch payload from IPFS
            raise NotImplemented
        

    def confirm_duplicate_update(self, update, update_hash_history):

        update_hash = sha256(jcs.canonicalize(update))
        # Note: version starts at 1, index starts at 0
        update_hash_index = update["targetVersionId"] - 2
        historical_update_hash = update_hash_history[update_hash_index]
        if (historical_update_hash != update_hash):
            raise Exception("Late Publishing Error")
        return    

        
    def apply_did_update(self, contemporary_document, update):
        # Retrieve the verification method used to secure the proof from the contemporary DID document
        capability_id = update["proof"]["capability"]
        document_to_update = contemporary_document.model_copy(deep=True)

        root_capability = self.dereference_root_capability(capability_id)
        
        proof_vm_id = update["proof"]["verificationMethod"]
        btc1_identifier = document_to_update.id
        verification_method = None
        for vm in document_to_update.verification_method:
            vm_id = vm.id
            if vm_id[0] == "#":
                vm_id = f"{btc1_identifier}{vm_id}"
            if vm_id == proof_vm_id:
                print("Verification Method found", vm)
                verification_method = vm.serialize()
        if verification_method == None:
            raise Exception("Invalid Proof on Update Payload")
        multikey = SchnorrSecp256k1Multikey.from_verification_method(verification_method)

        # Instantiate a schnorr-secp256k1-2025 cryptosuite instance.
        cryptosuite = Bip340JcsCryptoSuite(multikey)
        di_proof = DataIntegrityProof(cryptosuite=cryptosuite)

        mediaType = "application/json"

        expected_proof_purpose = "capabilityInvocation"

        update_bytes = json.dumps(update)

        verificationResult = di_proof.verify_proof(mediaType, update_bytes, expected_proof_purpose, None, None)

        if not verificationResult["verified"]:
            raise Exception("invalidUpdateProof")

        target_did_document = copy.deepcopy(document_to_update.serialize())

        update_patch = update["patch"]

        patch = jsonpatch.JsonPatch(update_patch)
        
        target_did_document = patch.apply(target_did_document)

        target_hash = bytes_to_str(base58.b58encode(sha256(jcs.canonicalize(target_did_document))))

        target_doc = Btc1Document.model_validate(target_did_document)
        
        serialzied_doc = target_doc.serialize()
        
        compare_dictionaries(serialzied_doc, target_did_document)
        
        
        test_hash = bytes_to_str(base58.b58encode(target_doc.canonicalize()))

        print(update["targetHash"], target_hash)
        if (target_hash != update["targetHash"]):
            raise Exception("LatePublishingError")
        
        if (target_hash != test_hash):
            raise Exception("LatePublishingError")

        return Btc1Document.deserialize(target_did_document)
    
    

    def dereference_root_capability(self, capability_id):
    
        components = capability_id.split(":")
        assert(len(components) == 4)
        assert(components[0] == "urn")
        assert(components[1] == "zcap")
        assert(components[2] == "root")
        uri_encoded_id = components[3]
        btc1Identifier = urllib.parse.unquote(uri_encoded_id)
        root_capability = {
            "@context": "https://w3id.org/zcap/v1",
            "id": capability_id,
            "controller": btc1Identifier,
            "invocationTarget": btc1Identifier
        }
        return root_capability

def compare_dictionaries(dict1, dict2):
    if len(dict1) != len(dict2):
        return False
    for key in dict1:
        if key not in dict2 or dict1[key] != dict2[key]:
            return False
    return True