from libbtc1.resolver import Btc1Resolver
import asyncio
import json

async def resolve_deterministic():
  
    test_folder_path = "TestVectors/regtest/x1qgcs38429dp7kyr5y90g3l94r6ky85pnppy9aggzgas2kdcldelrk3yfjrf"
  
    with open(f"{test_folder_path}/did.txt", 'r') as f:
        # Read the contents of the file into a variable
        did_to_resolve = f.read()
        # Print the names
        print(did_to_resolve)
      
    with open(f"{test_folder_path}/resolutionOptions.json") as f:
        resolution_options = json.load(f)
        print(resolution_options)

    resolver = Btc1Resolver(logging=True)
    print(resolver.logging)
    document = await resolver.resolve(did_to_resolve, resolution_options)

    print("Resolved Document")
    print(json.dumps(document.serialize(), indent=2))



asyncio.run(resolve_deterministic())