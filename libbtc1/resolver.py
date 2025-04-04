from buidl.ecc import S256Point
from buidl.tx import Tx
import re
from bitcoinrpc import BitcoinRPC

from pydid.doc import DIDDocument
from pydid.doc.builder import VerificationMethodBuilder
from pydid.verification_method import Multikey

from .bech32 import decode_bech32_identifier
from .verificationMethod import get_verification_method
from .did import decode_identifier, KEY, EXTERNAL, InvalidDidError
from .diddoc.builder import Btc1DIDDocumentBuilder
from .helper import canonicalize_and_hash
from .service import BeaconTypes, CID_AGGREGATE_BEACON, SINGLETON_BEACON, SMT_AGGREGATE_BEACON

CONTEXT = ["https://www.w3.org/ns/did/v1", "https://did-btc1/TBD/context"]


GENESIS_COINBASE = "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
COINBASE_TXIDS = [GENESIS_COINBASE, "0000000000000000000000000000000000000000000000000000000000000000"]

SINGLETON_BEACON_TYPE = "SingletonBeacon"
P2PKH = "p2pkh"
P2WPKH = "p2wpkh"
P2TR = "p2tr"


class Btc1Resolver():

    def __init__(self, rpc_endpoint, rpcuser, rpcpassword):
        self.bitcoinrpc = BitcoinRPC.from_config("http://localhost:18443", ("polaruser", "polarpass"))



    async def resolve(self, identifier, resolution_options=None):

        

        id_type, version, network, genesis_bytes = decode_identifier(identifier)

        
        blockchain_info = await self.bitcoinrpc.getblockchaininfo()
        chain = blockchain_info["chain"]
        if chain != network:
            raise Exception(f"RPC connected to incorrect chain {chain}")

        if id_type == KEY:
            initial_did_document = await self.resolve_deterministic(identifier, 
                                                        genesis_bytes, 
                                                        version, 
                                                        network)
        elif id_type == EXTERNAL:
            pass
        else:
            raise Exception("Invalid HRP")
        
        # TODO: Process Beacon Signals

        did_document = initial_did_document
        return did_document.serialize()



    def resolve_deterministic(self, btc1_identifier, key_bytes, version, network):

        pubkey = S256Point.parse_sec(key_bytes)

        builder = Btc1DIDDocumentBuilder.from_secp256k1_key(pubkey, network, version)

        did_document = builder.build()

        if btc1_identifier != did_document.id:
            raise InvalidDidError("identifier does not match, deterministic document id")

        return did_document
    

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

        target_document = self.traverse_blockchain_history(contemporary_document, 
                                                           contemporary_blockheight, 
                                                           current_version_id, 
                                                           request_version_id, 
                                                           target_blockheight, 
                                                           update_hash_history, 
                                                           signals_metadata, 
                                                           network)

        return target_document

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
                                          contemporary_document: DIDDocument, 
                                          contemporary_blockheight, 
                                          current_version_id, 
                                          target_version_id, 
                                          target_blockheight, 
                                          update_hash_history, 
                                          signals_metadata,
                                          network):
        contemporary_hash = canonicalize_and_hash(contemporary_document.serialize())      
        beacons = []
        for service in contemporary_document.service:
            if service.type in BeaconTypes:
                beacon = service.serialize()
                beacon["address"] = service.service_endpoint.replace("bitcoin:", "")
                
                beacons.append(service)

        next_signals = await self.find_next_signals(beacons, contemporary_blockheight, target_blockheight, network)

        contemporary_blockheight = next_signals["blockheight"]

        signals = next_signals["signals"]

        updates = self.process_beacon_signals(signals, signals_metadata)

    async def find_next_signals(self, beacons, contemporary_blockheight, target_blockheight, network):
        signals = []

        block = await self.bitcoinrpc.getblockhash(contemporary_blockheight)

        for txid in block["tx"]:
            if txid not in COINBASE_TXIDS:
                tx_hex = await self.bitcoinrpc.getrawtransaction(txid)
                tx = Tx.parse_hex(tx_hex)

                for tx_in in tx.tx_ins:
                    prev_txid = tx_in.prev_tx.hex()
                    prev_tx_hex = await self.bitcoinrpc.getrawtransaction(prev_txid)
                    prev_tx = Tx.parse_hex(prev_tx_hex)

                    spent_tx_output = prev_tx.tx_outs[tx_in.prev_index]
                    spent_tx_output_address = spent_tx_output.script_pubkey.address(network="regtest")

                    beacon_signal = None
                    for beacon in beacons:
                        if beacon["address"] == spent_tx_output_address:
                            beacon_signal = {
                                "beaconId": beacon["id"],
                                "beaconType": beacon["type"],
                                "tx": tx
                            }
                            signals.append(beacon_signal)
                            print("Found Beacon Signal", tx)
                            break
                    
                    if beacon_signal:
                        break

        if contemporary_blockheight == target_blockheight:
            next_signals = {
                "blockheight": contemporary_blockheight,
                "signals": signals
            }
            return next_signals
        
        if len(signals) == 0:
            next_signals = self.find_next_signals(beacons, contemporary_blockheight+1, target_blockheight, network)
        else:
            next_signals = {
                "blockheight": contemporary_blockheight,
                "signals": signals
            }

        return next_signals
    

    def process_beacon_signals(signals, signals_metadata):
        updates = []

        for signal in signals:
            type = signal["beaconType"]
            signal_tx = signal["tx"]
            signal_id = signal_tx.id()
            signal_sidecar_data = signals_metadata.get(signal_id)
            did_update_payload = None
            if type == SINGLETON_BEACON:
                did_update_payload = process_singleton_beacon_signal()
    

        


