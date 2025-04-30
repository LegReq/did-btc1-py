from libbtc1.resolver import Btc1Resolver
import asyncio
import json

async def resolve_example():

    did = "did:btc1:x1qgkyp87k3dhlxtw73xlddz9nqs297g9epxlnhuskwmk47sg73x2y76mqmst"

    resolution_options = {
        "sidecarData": {
  "did": "did:btc1:x1qgkyp87k3dhlxtw73xlddz9nqs297g9epxlnhuskwmk47sg73x2y76mqmst",
  "initialDocument": {
    "@context": [
      "https://www.w3.org/TR/did-1.1",
      "https://did-btc1/TBD/context"
    ],
    "id": "did:btc1:x1qgkyp87k3dhlxtw73xlddz9nqs297g9epxlnhuskwmk47sg73x2y76mqmst",
    "controller": [
      "did:btc1:x1qgkyp87k3dhlxtw73xlddz9nqs297g9epxlnhuskwmk47sg73x2y76mqmst"
    ],
    "verificationMethod": [
      {
        "id": "did:btc1:x1qgkyp87k3dhlxtw73xlddz9nqs297g9epxlnhuskwmk47sg73x2y76mqmst#key-0",
        "type": "Multikey",
        "controller": "did:btc1:x1qgkyp87k3dhlxtw73xlddz9nqs297g9epxlnhuskwmk47sg73x2y76mqmst",
        "publicKeyMultibase": "zQ3shWNTDXbwtvMJ9v31xE2H4PrNEaz7MhFPQUG2fXwYzegaX"
      },
      {
        "id": "did:btc1:x1qgkyp87k3dhlxtw73xlddz9nqs297g9epxlnhuskwmk47sg73x2y76mqmst#key-1",
        "type": "Multikey",
        "controller": "did:btc1:x1qgkyp87k3dhlxtw73xlddz9nqs297g9epxlnhuskwmk47sg73x2y76mqmst",
        "publicKeyMultibase": "zQ3shdp5Jh1TXEDwDaWB9e8fNHk9TpaTZoKrCJzN1UQeiedA3"
      }
    ],
    "authentication": [
      "did:btc1:x1qgkyp87k3dhlxtw73xlddz9nqs297g9epxlnhuskwmk47sg73x2y76mqmst#key-0"
    ],
    "capabilityInvocation": [
      "did:btc1:x1qgkyp87k3dhlxtw73xlddz9nqs297g9epxlnhuskwmk47sg73x2y76mqmst#key-1"
    ],
    "capabilityDelegation": [
      "did:btc1:x1qgkyp87k3dhlxtw73xlddz9nqs297g9epxlnhuskwmk47sg73x2y76mqmst#key-1"
    ],
    "service": [
      {
        "id": "did:btc1:x1qgkyp87k3dhlxtw73xlddz9nqs297g9epxlnhuskwmk47sg73x2y76mqmst#service-0",
        "type": "SingletonBeacon",
        "serviceEndpoint": "bitcoin:bcrt1qretzk5u8f4w44k5yjk49dt8fjgugxjmfcddr9l"
      }
    ]
  },
  "signalsMetadata": {
    "f3311b226131451dcc286ed2f5c242af5af00bfd614ee70f1feaeb4aef6a3c8c": {
      "updatePayload": {
        "@context": [
          "https://w3id.org/security/v2",
          "https://w3id.org/zcap/v1",
          "https://w3id.org/json-ld-patch/v1"
        ],
        "patch": [
          {
            "op": "add",
            "path": "/service/1",
            "value": {
              "id": "did:btc1:x1qgkyp87k3dhlxtw73xlddz9nqs297g9epxlnhuskwmk47sg73x2y76mqmst#service-1",
              "type": "SingletonBeacon",
              "serviceEndpoint": "bitcoin:bcrt1qretzk5u8f4w44k5yjk49dt8fjgugxjmfcddr9l"
            }
          }
        ],
        "sourceHash": "88R6dKcGcLM2MrDTGXHzFAAK2nPu1digEKo8YSS7xFuP",
        "targetHash": "GWH4y3vz99k4rnzGZ6U1yJwpFPDwfx2Z9apgpKACCxwb",
        "targetVersionId": 2,
        "proof": {
          "type": "DataIntegrityProof",
          "cryptosuite": "bip340-jcs-2025",
          "verificationMethod": "did:btc1:x1qgkyp87k3dhlxtw73xlddz9nqs297g9epxlnhuskwmk47sg73x2y76mqmst#key-1",
          "proofPurpose": "capabilityInvocation",
          "capability": "urn:zcap:root:did%3Abtc1%3Ax1qgkyp87k3dhlxtw73xlddz9nqs297g9epxlnhuskwmk47sg73x2y76mqmst",
          "capabilityAction": "Write",
          "@context": [
            "https://w3id.org/security/v2",
            "https://w3id.org/zcap/v1",
            "https://w3id.org/json-ld-patch/v1"
          ],
          "proofValue": "z4L74cQpN6GEhBG4U29qQkTxP4Mdb6WXYNXvUhZE6TUNEBHxirmHcVPvRxf3gFLrPVcogXujWGjQXFDiNSidf6Mvj"
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