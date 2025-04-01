
from .did import encode_identifier, KEY, EXTERNAL, NETWORKS, VERSIONS
from .resolver import resolve

def create_deterministic(public_key, network=None, version=None):
    if network is not None and network not in NETWORKS:
        raise Exception(f"Invalid Network : {network}")
    
    if version is not None and version not in VERSIONS:
        raise Exception(f"Invalid Version : {version}")

    sec_pubkey = public_key.sec()

    did_btc1 = encode_identifier(KEY, version, network, sec_pubkey)
    did_document = resolve(did_btc1, {})

    return did_btc1, did_document