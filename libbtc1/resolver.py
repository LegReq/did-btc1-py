import re

def resolve(identifier, resolution_options):
    identifier_components = parse_btc1_identifier(identifier)


def parse_btc1_identifier(identifier):
    chunks = identifier.split(":")
    identifier_components = {}

    match = re.search(r"^did:btc1:(?:(\d+):)?(?:(mainnet|signet|testnet|regtest):)?((k1|x1)[023456789acdefghjklmnpqrstuvwxyz]*)$")

    # if len(chunks) < 3 or chunks > 5:
    #     raise "Invalid DID"

    # assert chunks[0] == "did"
    # assert chunks[1] == "btc1"

    # if len(chunks) == 3:
    #     identifier_components["network"] = "mainnet"
    #     identifier_components["version"] = 1
    #     bech32_encoding = chunks[2]
    # elif len(chunks) == 4:






