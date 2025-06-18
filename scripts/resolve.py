from libbtc1.resolver import Btc1Resolver
import asyncio
import json
from buidl.helper import sha256, bytes_to_str
import base58
import jcs


async def resolve_signet():
  
    networkDefinitions = {  
        "regtest": {
            "btc_network": "regtest",
            "esplora_api": "http://localhost:3000",
        },
        "mutinynet": {
            "btc_network": "signet",
            "esplora_api": "https://mutinynet.com/api",
        },
        "signet": {
            "btc_network": "signet",
            "esplora_api": "https://mempool.space/signet/api",
        }
    }

    # test_folder_path = "TestVectors/regtest/k1qgp5h79scv4sfqkzak5g6y89dsy3cq0pd2nussu2cm3zjfhn4ekwrucc4q7t7"
    test_folder_path = "TestVectors/signet/x1qyj23twdpn927d5ky2f5ulgmr9uudq2pd08gxy05fdjzxvfclzn2zazps8w"

    with open(f"{test_folder_path}/did.txt", 'r') as f:
        # Read the contents of the file into a variable
        did_to_resolve = f.read()
        # Print the names
        print(did_to_resolve)
      
    with open(f"{test_folder_path}/resolutionOptions.json") as f:
        resolution_options = json.load(f)
        print(resolution_options)


    # with open(f"{test_folder_path}/targetDidDocument.json") as f:
    #     initial_document = json.load(f)
    #     print(initial_document)

    

    resolver = Btc1Resolver(networkDefinitions=networkDefinitions, logging=True)
    print(resolver.logging)
    document = await resolver.resolve(did_to_resolve, resolution_options)

    print("Resolved Document")
    print(json.dumps(document.serialize(), indent=2))



asyncio.run(resolve_signet())