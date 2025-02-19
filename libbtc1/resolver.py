from buidl.ecc import S256Point
import re
from .bech32 import decode_bech32_identifier
from .verificationMethod import get_verification_method

CONTEXT = ["https://www.w3.org/ns/did/v1", "https://did-btc1/TBD/context"]

SINGLETON_BEACON_TYPE = "SingletonBeacon"
P2PKH = "p2pkh"
P2WPKH = "p2wpkh"
P2TR = "p2tr"


def resolve(identifier, resolution_options=None):
    identifier_components = parse_btc1_identifier(identifier)

    hrp = identifier_components["hrp"]
    if hrp == "k":
        initial_did_document = resolve_deterministic(identifier, 
                                                     identifier_components["genesis_bytes"], 
                                                     identifier_components["version"], 
                                                     identifier_components["network"])
    elif hrp == "x":
        pass
    else:
        raise "Invalid HRP"
    
    # TODO: Process Beacon Signals

    did_document = initial_did_document
    return did_document

def parse_btc1_identifier(identifier):
    identifier_components = {}

    match = re.match(r"^did:btc1:(?:(\d+):)?(?:(mainnet|signet|testnet|regtest):)?((k1|x1)[023456789acdefghjklmnpqrstuvwxyz]*)$", identifier)

    try:
        # did = match.group()
        identifier_components["version"] = match.group(1) or 1
        identifier_components["network"] = match.group(2) or "mainnet"
        bech32_encoding = match.group(3)
        hrp, genesis_bytes = decode_bech32_identifier(bech32_encoding)
        identifier_components["hrp"] = hrp
        identifier_components["genesis_bytes"] = genesis_bytes
    except:
        raise "invalidDID Exception"


    return identifier_components





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
