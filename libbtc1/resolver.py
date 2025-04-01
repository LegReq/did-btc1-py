from buidl.ecc import S256Point
import re

from pydid.doc.builder import VerificationMethodBuilder
from pydid.verification_method import Multikey

from .bech32 import decode_bech32_identifier
from .verificationMethod import get_verification_method
from .did import decode_identifier, KEY, EXTERNAL
from .diddoc.builder import Btc1DIDDocumentBuilder
from .multikey import get_public_key_multibase

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
    return did_document.serialize()



def resolve_deterministic(btc1_identifier, key_bytes, version, network):

    builder = Btc1DIDDocumentBuilder(btc1_identifier, CONTEXT, controller=btc1_identifier)

    vm_id = "#initialKey"

    public_key_multibase = get_public_key_multibase(key_bytes)

    verificationMethod = builder.verification_method.add(Multikey, vm_id, controller=btc1_identifier, public_key_multibase=public_key_multibase)

    # vm = get_verification_method(btc1_identifier, initial_key, vm_id)

    # did_document["verificationMethod"] = [vm]

    builder.authentication.reference(verificationMethod.id)
    builder.assertion_method.reference(verificationMethod.id)
    builder.capability_delegation.reference(verificationMethod.id)
    builder.capability_invocation.reference(verificationMethod.id)

    if network == "bitcoin":
        network = "mainnet"
    if network == "testnet3" or network == "testnet4":
        network = "testnet"
    elif isinstance(network, int):
        # TODO: what should network be when custom?
        network = "signet"

    pubkey = S256Point.parse_sec(key_bytes)

    p2pkh_address = pubkey.p2pkh_script().address(network)
    builder.service.add_singleton_beacon("#initialP2PKH", p2pkh_address)

    p2wpkh_address = pubkey.p2wpkh_address(network=network)
    builder.service.add_singleton_beacon("#initialP2WPKH", p2wpkh_address)

    p2tr_address = pubkey.p2tr_address(network=network)
    builder.service.add_singleton_beacon("#initialP2TR", p2tr_address)

    did_document = builder.build()

    return did_document
