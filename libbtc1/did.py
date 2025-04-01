from buidl.ecc import S256Point
import math

from .bech32 import encode_bech32_identifier, decode_bech32_identifier
from .resolver import resolve
from.verificationMethod import get_verification_method

from .error import InvalidDidError

BITCOIN="bitcoin"
SIGNET="signet"
TESTNET3="testnet3"
TESTNET4="testnet4"
REGTEST="regtest"

NETWORKS = [BITCOIN, SIGNET, REGTEST, TESTNET3, TESTNET4]

VERSIONS = [1]

EXTERNAL = "external"
KEY = "key"


id_type_to_hrp = {}

id_type_to_hrp[EXTERNAL] = "x"
id_type_to_hrp[KEY] = "k"

hrp_to_id_type = {v: k for k, v in id_type_to_hrp.items()}

network_map = {
    0x0: "bitcoin",
    0x1: "signet",
    0x2: "regtest",
    0x3: "testnet3",
    0x4: "testnet4",
}



P2PKH = "p2pkh"
P2WPKH = "p2wpkh"
P2TR = "p2tr"

SINGLETON_BEACON_TYPE = "SingletonBeacon"

CONTEXT = ["https://www.w3.org/ns/did/v1", "https://did-btc1/TBD/context"]





def encode_identifier(id_type, version, network, genesis_bytes):
    if id_type not in [EXTERNAL, KEY]:
        raise InvalidDidError()
    
    if version != 1:
        raise InvalidDidError()

<<<<<<< HEAD
    versionStr = "" if version == None else f":{version}"
    networkStr = "" if network == None else f":{network}"

    sec_pubkey = public_key.sec()
    bech32_id = encode_bech32_identifier(KEY, sec_pubkey)

    did_btc1 = f"did:btc1{versionStr}{networkStr}:{bech32_id}"
    resolution_options = {}
    did_document = resolve(did_btc1, resolution_options)

    return did_btc1, did_document



# def resolve(did_btc1):
#     identifier_components = did_btc1.split(":")

#     if len(identifier_components) < 3:
#         raise Exception(f"Invalid DID: {did_btc1}")
    
#     assert identifier_components[0] == "did", f"Invalid DID: {did_btc1}. No did scheme."
#     assert identifier_components[1] == "btc1", f"Invalid DID: {did_btc1}. Method is not btc1."
    
#     version = None
#     network = None
#     bech32_id = None

#     if len(identifier_components) == 3:
#         bech32_id = identifier_components[2]
#         version = 1
#         network = "mainnet"
#     elif len(identifier_components) == 4:
#         try:
#             version = int(identifier_components[2])
#             network = MAINNET
#         except:
#             network = identifier_components[2]
#             version = 1

#         bech32_id = identifier_components[3]
#     elif len(identifier_components) == 5:
#         version = int(identifier_components[1])
#         network = identifier_components[3]
#         bech32_id = identifier_components[4]
#     else:
#         raise Exception(f"Invalid DID: {did_btc1}. Too many identifier components.")

#     assert version in VERSIONS, f"Invalid DID: {did_btc1}. Version {version} not recognised."
#     assert network in NETWORKS, f"Invalid DID: {did_btc1}. Network {network} not recognised."

#     type, identifier_bytes = decode_bech32_identifier(bech32_id)

#     if type == KEY:
#         initial_did_document = resolve_deterministic(did_btc1, identifier_bytes, version, network)
#     elif type == EXTERNAL:
#         raise NotImplemented
    
#     # TODO: Process Beacon Signals

#     did_document = initial_did_document
    
#     return did_document
=======
    network_num = None
    if network not in NETWORKS:
        try:
            number = int(network)
            if number < 0:
                raise InvalidDidError()
            network_num = number + 7
        except ValueError:
            raise InvalidDidError(f"Network not recognised {network}")
    else:
        network_num = NETWORKS.index(network)

    if id_type == KEY:
        try:
            S256Point.parse_sec(genesis_bytes)
        except:
            raise InvalidDidError("Genesis bytes is not a valid compressed secp256k1 public key")

    hrp = id_type_to_hrp[id_type]
    
    nibbles = []
    f_count = math.floor((version - 1) / 15)

    for i in range(f_count):
        nibbles.append(15)
        
    nibbles.append((version - 1) % 15)
    nibbles.append(network_num)

    if len(nibbles) % 2 == 1:
        nibbles.append(0)


    nibble_range = int(len(nibbles) / 2) - 1
    data_bytes = bytearray()

    if f_count == 0:
        concat = (nibbles[2 * 0] << 4) | nibbles[2 * 0 + 1]
        data_bytes.append((nibbles[2 * 0] << 4) | nibbles[2 * 0 + 1])
    else:
        for index in range(nibble_range):
            print(index)
            raise NotImplementedError()


    data_bytes += bytearray(genesis_bytes)

    identifier = "did:btc1:"

    encoded_string = encode_bech32_identifier(hrp, data_bytes)

    identifier += encoded_string

    return identifier



def decode_identifier(identifier):
    components = identifier.split(":")
    if len(components) != 3:
        raise InvalidDidError()
    
    if components[0] != "did":
        raise InvalidDidError()

    if components[1] != "btc1":
        raise Exception("methodNotSupported")
    
    encoded_string = components[2]

    hrp, data_bytes = decode_bech32_identifier(encoded_string)

    id_type = hrp_to_id_type.get(hrp)
    
    if id_type is None:
        raise InvalidDidError()
    
    version = 1

    byte_index = 0

    nibbles_consumed = 0

    current_byte = data_bytes[byte_index]

    version_nibble = current_byte >> 4
>>>>>>> 038d29e (implement new identifier syntax)


    while version_nibble == 0xF:
        version += 15
        # TODO
        if nibbles_consumed % 2 == 0:
            version_nibble = current_byte & 0x0F
        else:
            byte_index += 1
            current_byte = data_bytes[byte_index]
            version_nibble = current_byte >> 4
        nibbles_consumed += 1

<<<<<<< HEAD
# def resolve_deterministic(did_btc1, key_bytes, version, network):
#     did_document = {}
#     did_document["id"] = did_btc1
#     did_document["@context"] = CONTEXT

#     initial_key = S256Point.parse_sec(key_bytes)

#     vm_id = "#initialKey"
#     vm = get_verification_method(did_btc1, initial_key, vm_id)

#     did_document["verificationMethod"] = [vm]

#     did_document["authentication"] = [vm_id]
#     did_document["assertionMethod"] = [vm_id]
#     did_document["capabilityInvocation"] = [vm_id]
#     did_document["capabilityDelegation"] = [vm_id]

#     did_document["service"] = deterministically_generate_beacon_services(initial_key, network)
#     return did_document

# def deterministically_generate_beacon_services(pubkey: S256Point, network):
#     p2pkh_beacon = generate_singleton_beacon_service(pubkey, "#initial_p2pkh",P2PKH,network)
#     p2wpkh_beacon = generate_singleton_beacon_service(pubkey, "#initial_p2wpkh",P2WPKH,network)
#     p2tr_beacon = generate_singleton_beacon_service(pubkey, "#initial_p2tr",P2TR,network)
#     service = [p2pkh_beacon, p2wpkh_beacon, p2tr_beacon]
#     return service

# def generate_singleton_beacon_service(pubkey: S256Point, service_id, address_type, network):
#     if address_type == P2PKH:
#         address = pubkey.p2pkh_script().address(network)
#     elif address_type == P2WPKH:
#         address = pubkey.p2wpkh_address(network=network)
#     elif address_type == P2TR:
#         address = pubkey.p2tr_address(network=network)
#     else:
#         raise Exception(f"Address Type {address_type} Not recognised")
    
#     bip21_address_uri = f"bitcoin:{address}"
#     beacon_service = {
#         "id": service_id,
#         "type": SINGLETON_BEACON_TYPE,
#         "serviceEndpoint": bip21_address_uri
#     }

#     return beacon_service
=======
    version += version_nibble
    nibbles_consumed += 1

    if nibbles_consumed % 2 == 0:
        byte_index += 1
        current_byte = data_bytes[byte_index]
        network_nibble = current_byte >> 4
    else:
        network_nibble = current_byte & 0x0F

    nibbles_consumed += 1
    network_value = network_nibble

    network = network_map.get(network_value)

    if not network:
        if 0x8 <= network_value <= 0xF:
            network = network_value - 7
        else:
            raise InvalidDidError()

    if nibbles_consumed % 2 == 1:
        filler_nibble = current_byte & 0x0F
        if filler_nibble != 0:
            raise InvalidDidError()
        
    genesis_bytes = data_bytes[byte_index+1:]

    if id_type == KEY:
        try:
            S256Point.parse_sec(genesis_bytes)
        except:
            raise InvalidDidError()
    
    return id_type, version, network, genesis_bytes
        



>>>>>>> 038d29e (implement new identifier syntax)


