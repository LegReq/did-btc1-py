from libbtc1.resolver import Btc1Resolver
import asyncio
import json

async def resolve_deterministic():
  
    test_folder_path = "TestVectors/k1qgpswh5adnhrvk9vpppgcx08k4eek75c52dr9pcvu2zt5zgakartekc4uzg54"
  
    with open(f"{test_folder_path}/did.txt", 'r') as f:
        # Read the contents of the file into a variable
        did_to_resolve = f.read()
        # Print the names
        print(did_to_resolve)
      
    with open(f"{test_folder_path}/resolutionOptions.json") as f:
        resolution_options = json.load(f)
        print(resolution_options)



    rpc_endpoint = "http://localhost:18443"
    resolver = Btc1Resolver(rpc_endpoint=rpc_endpoint, rpcuser="polaruser", rpcpassword="polarpass", logging=True)
    print(resolver.logging)
    document = await resolver.resolve(did_to_resolve, resolution_options)

    print("Resolved Document")
    print(json.dumps(document.serialize(), indent=2))



asyncio.run(resolve_deterministic())