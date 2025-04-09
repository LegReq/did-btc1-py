from libbtc1.resolver import Btc1Resolver
import asyncio
import json

async def resolve_example():

    did = "did:btc1:k1qgpjmuyrw6f66tvcer3q8g8cqphyznew4cs0ua3fv9mqdg5lcsvwltq3e67u6"

    resolution_options = {
        "sidecarData": {
            "did": "did:btc1:k1qgpjmuyrw6f66tvcer3q8g8cqphyznew4cs0ua3fv9mqdg5lcsvwltq3e67u6",
            "signalsMetadata": {
                "6a1d48e11a6647db2f173e0dfe4d3399db62cac9d6d6b5c02e140a66e28e26ba": {
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
                        "id": "did:btc1:k1qgpjmuyrw6f66tvcer3q8g8cqphyznew4cs0ua3fv9mqdg5lcsvwltq3e67u6#service-0",
                        "type": "SingletonBeacon",
                        "serviceEndpoint": "bitcoin:bcrt1pvgyvzsejga0gxq6vgkwzx0r4ta6ek3un3xhzxfaueza4jaq2pqlqm9635r"
                        }
                    }
                    ],
                    "sourceHash": "97gWENcfBgX7zgsGzAYyWGqGrJiD9ggRDrzhTpPvbkrE",
                    "targetHash": "AbDiGV3QY5rQLiidvAcu988QzpRqC44EqAWVdF6qbqcc",
                    "targetVersionId": 2,
                    "proof": {
                    "type": "DataIntegrityProof",
                    "cryptosuite": "bip340-jcs-2025",
                    "verificationMethod": "did:btc1:k1qgpjmuyrw6f66tvcer3q8g8cqphyznew4cs0ua3fv9mqdg5lcsvwltq3e67u6##initialKey",
                    "proofPurpose": "capabilityInvocation",
                    "capability": "urn:zcap:root:did%3Abtc1%3Ak1qgpjmuyrw6f66tvcer3q8g8cqphyznew4cs0ua3fv9mqdg5lcsvwltq3e67u6",
                    "capabilityAction": "Write",
                    "@context": [
                        "https://w3id.org/security/v2",
                        "https://w3id.org/zcap/v1",
                        "https://w3id.org/json-ld-patch/v1"
                    ],
                    "proofValue": "z4jzE16rDoxevZrFRbA7qEZvQ9XUDrb5H5kkUHSRYukM2KBKckk6PhJNM4eHzkWYhjzq1Eo2Lj76J2a8Zmyvoz68P"
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