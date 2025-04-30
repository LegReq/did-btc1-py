from libbtc1.resolver import Btc1Resolver
import asyncio
import json

async def resolve_example():

    did = "did:btc1:k1qgpdzwmyqnm2q6cegx8r7km9np0zu38j3s2jytknwyfsrl5rj0we8eqmy5e0a"

    resolution_options = {
  "sidecarData": {
  "did": "did:btc1:k1qgpdzwmyqnm2q6cegx8r7km9np0zu38j3s2jytknwyfsrl5rj0we8eqmy5e0a",
  "signalsMetadata": {
    "2546e26ef3cb86dc04e334a18131729b5c3bb0388eab0dfaa60fbf3fb0e49b2a": {
      "updatePayload": {
        "@context": [
          "https://w3id.org/security/v2",
          "https://w3id.org/zcap/v1",
          "https://w3id.org/json-ld-patch/v1"
        ],
        "patch": [
          {
            "op": "add",
            "path": "/service/3",
            "value": {
              "id": "did:btc1:k1qgpdzwmyqnm2q6cegx8r7km9np0zu38j3s2jytknwyfsrl5rj0we8eqmy5e0a#service-0",
              "type": "SingletonBeacon",
              "serviceEndpoint": "bitcoin:bcrt1pvpmyqhfhz29u99jyktjsladm3qrjhwle6yk9a58ckcygp88th9eqdg98ad"
            }
          }
        ],
        "sourceHash": "9PA4kU5n7DziJjGVYV1nz6wuDwbBDU2j1SLZkfZH1geS",
        "targetHash": "2vs5UtjAfTywuHwh9g7QwpSt99MddAhVo9qeqLGwJGEJ",
        "targetVersionId": 2,
        "proof": {
          "type": "DataIntegrityProof",
          "cryptosuite": "bip340-jcs-2025",
          "verificationMethod": "did:btc1:k1qgpdzwmyqnm2q6cegx8r7km9np0zu38j3s2jytknwyfsrl5rj0we8eqmy5e0a#initialKey",
          "proofPurpose": "capabilityInvocation",
          "capability": "urn:zcap:root:did%3Abtc1%3Ak1qgpdzwmyqnm2q6cegx8r7km9np0zu38j3s2jytknwyfsrl5rj0we8eqmy5e0a",
          "capabilityAction": "Write",
          "@context": [
            "https://w3id.org/security/v2",
            "https://w3id.org/zcap/v1",
            "https://w3id.org/json-ld-patch/v1"
          ],
          "proofValue": "z2bcsYyUbQQQWyexDr5ZN5TjQ3apxH26McyWdjZEoDpsjW6j1r6614TY1k2wbWDk5vT4GyT5nwLb4DcKZWTehfq5Z"
        }
      }
    }
  }
}
}

    rpc_endpoint = "http://localhost:18443"
    resolver = Btc1Resolver(rpc_endpoint=rpc_endpoint, rpcuser="polaruser", rpcpassword="polarpass")

    document = await resolver.resolve(did, resolution_options)

    print("Resolved Document")
    print(json.dumps(document.serialize(), indent=2))



asyncio.run(resolve_example())