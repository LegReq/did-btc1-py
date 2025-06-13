from libbtc1.resolver import Btc1Resolver
import asyncio
import json
from buidl.helper import sha256, bytes_to_str
import base58
import jcs


async def resolve_signet():
  
    test_folder_path = "TestVectors/mutinynet/k1qypdnfyh7j8z87wk3vylqaz9t8psnkws8k5e2ccl9c0zqwwt5uyjeeg7f3knj"
  
    with open(f"{test_folder_path}/did.txt", 'r') as f:
        # Read the contents of the file into a variable
        did_to_resolve = f.read()
        # Print the names
        print(did_to_resolve)
      
    with open(f"{test_folder_path}/resolutionOptions.json") as f:
        resolution_options = json.load(f)
        print(resolution_options)


    with open(f"{test_folder_path}/targetDocument.json") as f:
        initial_document = json.load(f)
        print(initial_document)

    contemporary_hash = sha256(jcs.canonicalize(initial_document))
    # source_hash = resolution_options["sourceHash"]
    print("Contemporary Hash", bytes_to_str(base58.b58encode(contemporary_hash)))

    rpc_endpoint = "http://localhost:18443"
    resolver = Btc1Resolver(rpc_endpoint=rpc_endpoint, rpcuser="polaruser", rpcpassword="polarpass", esplora_base="https://mutinynet.com/api", logging=False)
    print(resolver.logging)
    document = await resolver.resolve(did_to_resolve, resolution_options)

    print("Resolved Document")
    print(json.dumps(document.serialize(), indent=2))



asyncio.run(resolve_signet())