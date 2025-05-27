import jcs
import ipfs_cid
from buidl.helper import sha256
from multiformats import cid
from multiformats import multihash

intermediate_doc = {
  "@context": [
    "https://www.w3.org/TR/did-1.1",
    "https://did-btc1/TBD/context"
  ],
  "id": "did:btc1:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "controller": [
    "did:btc1:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  ],
  "verificationMethod": [
    {
      "id": "did:btc1:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx#key-0",
      "type": "Multikey",
      "controller": "did:btc1:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "publicKeyMultibase": "zQ3shtiWU2YmQJnwWBZ69DtWrLck6VWajEs64joMqRS5KXcZ5"
    },
    {
      "id": "did:btc1:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx#key-1",
      "type": "Multikey",
      "controller": "did:btc1:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "publicKeyMultibase": "zQ3shNmrN4M1vcMtT57dfyYvVPhSVnzo8QUgcz4E5ZzJSzi4w"
    }
  ],
  "authentication": [
    "did:btc1:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx#key-0"
  ],
  "capabilityInvocation": [
    "did:btc1:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx#key-1"
  ],
  "capabilityDelegation": [
    "did:btc1:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx#key-1"
  ],
  "service": [
    {
      "id": "did:btc1:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx#service-0",
      "type": "SingletonBeacon",
      "serviceEndpoint": "bitcoin:bcrt1qser62ssp8n49yh5famt93m7tdgwqv76r3j9d5n"
    }
  ]
}

canonicalBytes = jcs.canonicalize(intermediate_doc)
print(canonicalBytes)
import json
print(json.loads(canonicalBytes))
hash_bytes = sha256(jcs.canonicalize(intermediate_doc))

cid1 = ipfs_cid.cid_sha256_wrap_digest(hash_bytes)
cid2 = ipfs_cid.cid_sha256_hash(canonicalBytes)
print(cid1)
print(cid2)
print("bafkreibhgnw4baa33xtdr3tj2nxbc5cuag5si57dff5y4sufokfyvz7fwi")
print("bafkreibhgnw4baa33xtdr3tj2nxbc5cuag5si57dff5y4sufokfyvz7fwi")

multi = multihash.digest(canonicalBytes, "sha2-256").hex()
cid3 = cid.CID("base32", 1, "raw", multi)

print(str(cid3))