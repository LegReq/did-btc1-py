from buidl.ecc import S256Point
import re
from .bech32 import decode_bech32_identifier
from .verificationMethod import get_verification_method
from .did import decode_identifier, KEY, EXTERNAL

CONTEXT = ["https://www.w3.org/ns/did/v1", "https://did-btc1/TBD/context"]

SINGLETON_BEACON_TYPE = "SingletonBeacon"
P2PKH = "p2pkh"
P2WPKH = "p2wpkh"
P2TR = "p2tr"


def resolve(identifier, resolution_options=None):
    id_type, version, network, genesis_bytes = decode_identifier(identifier)

    if id_type == KEY:
        initial_did_document = resolve_deterministic(identifier, 
                                                    genesis_bytes, 
                                                    version, 
                                                   network)
    elif id_type == EXTERNAL:
        pass
    else:
        raise "Invalid HRP"
    
    # TODO: Process Beacon Signals

    did_document = initial_did_document
    return did_document



def resolve_deterministic(btc1_identifier, key_bytes, version, network):
    did_document = {}
    did_document["id"] = btc1_identifier
    did_document["@context"] = CONTEXT

    initial_key = S256Point.parse_sec(key_bytes)

    vm_id = "#initialKey"
    vm = get_verification_method(btc1_identifier, initial_key, vm_id)

    did_document["verificationMethod"] = [vm]

    did_document["authentication"] = [vm_id]
    did_document["assertionMethod"] = [vm_id]
    did_document["capabilityInvocation"] = [vm_id]
    did_document["capabilityDelegation"] = [vm_id]

    did_document["service"] = deterministically_generate_beacon_services(initial_key, network)
    return did_document


def deterministically_generate_beacon_services(pubkey: S256Point, network):

    if network == "testnet3" or network == "testnet4":
        network = "testnet"
    elif isinstance(network, int):
        # TODO: what should network be when custom?
        network = "signet"
    

    p2pkh_beacon = generate_singleton_beacon_service(pubkey, "#initial_p2pkh", 
                                                     P2PKH, network)
    p2wpkh_beacon = generate_singleton_beacon_service(pubkey, "#initial_p2wpkh", 
                                                      P2WPKH, network)
    p2tr_beacon = generate_singleton_beacon_service(pubkey, "#initial_p2tr", 
                                                    P2TR, network)
    service = [p2pkh_beacon, p2wpkh_beacon, p2tr_beacon]
    return service


def generate_singleton_beacon_service(pubkey: S256Point, service_id, 
                                      address_type, network):
    if address_type == P2PKH:
        address = pubkey.p2pkh_script().address(network)
    elif address_type == P2WPKH:
        address = pubkey.p2wpkh_address(network=network)
    elif address_type == P2TR:
        address = pubkey.p2tr_address(network=network)
    else:
        raise Exception(f"Address Type {address_type} Not recognised")
    
    bip21_address_uri = f"bitcoin:{address}"
    beacon_service = {
        "id": service_id,
        "type": SINGLETON_BEACON_TYPE,
        "serviceEndpoint": bip21_address_uri
    }

    return beacon_service
