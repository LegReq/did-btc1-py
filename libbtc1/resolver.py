import re
from .bech32 import decode_bech32_identifier

def resolve(identifier, resolution_options):
    identifier_components = parse_btc1_identifier(identifier)


def parse_btc1_identifier(identifier):
    identifier_components = {}

    match = re.match(r"^did:btc1:(?:(\d+):)?(?:(mainnet|signet|testnet|regtest):)?((k1|x1)[023456789acdefghjklmnpqrstuvwxyz]*)$")

    try:
        did = match.group()
        identifier_components["version"] = match.group(1) or 1
        identifier_components["network"] = match.group(2) or "mainnet"
        bech32_encoding = match.group(3)
        hrp, genesis_bytes = decode_bech32_identifier(bech32_encoding)
        identifier_components["hrp"] = hrp
        identifier_components["genesis_bytes"] = genesis_bytes
    except:
        
        print("invalidDID Exception") 


    return identifier_components





