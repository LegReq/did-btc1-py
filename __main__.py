
import json
from pydid.doc import DIDDocument
from buidl.ecc import S256Point, PrivateKey, N
import secrets
import jcs


from buidl.helper import big_endian_to_int, sha256

from libbtc1.did import encode_identifier, decode_identifier
from libbtc1.resolver import resolve, resolve_deterministic
from libbtc1.service import SingletonBeaconService
from libbtc1.diddoc.builder import Btc1DIDDocumentBuilder


def main():
    # did_btc1 = "did:btc1:k1q2ddta4gt5n7u6d3xwhdyua57t6awrk55ut82qvurfm0qnrxx5nw7vnsy65"
    # did_document = resolve(did_btc1, {})
    # print(did_document)

    # document = DIDDocument.from_json(json.dumps(did_document))
    # print(document.id)
    # builder = Btc1DIDDocumentBuilder.from_doc(document)

    # res = builder.build().to_json()

    # print("Final build document", res)

    secret = big_endian_to_int(secrets.token_bytes(32)) % N

    private_key = PrivateKey(secret)

    pub_key = private_key.point

    genesis_bytes = pub_key.sec()

    print(genesis_bytes.hex())

    identifier = encode_identifier("key", 1, 5, genesis_bytes)

    print(identifier)

    did_document = resolve(identifier)

    # print(json.dumps(did_document,))


    external_document = {"id": "did:btc1:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "@context": ["https://www.w3.org/ns/did/v1", "https://did-btc1/TBD/context"], "verificationMethod": [{"id": "#initialKey", "type": "Multikey", "controller": "did:btc1:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "publicKeyMultibase": "z66Pmhojmn1jLPcLCLkK5Sv3Cjz5NxvA6Fn4mALJXhNzpgfC"}], "authentication": ["#initialKey"], "assertionMethod": ["#initialKey"], "capabilityInvocation": ["#initialKey"], "capabilityDelegation": ["#initialKey"], "service": [{"id": "#initial_p2pkh", "type": "SingletonBeacon", "serviceEndpoint": "bitcoin:mfzBTMBvzyG4KXJeWDyGPq4Jbv3bhQbNvw"}, {"id": "#initial_p2wpkh", "type": "SingletonBeacon", "serviceEndpoint": "bitcoin:bcrt1qq5nrwuhfqhte96pnc0kh0p9kxsnxnmdnw22pag"}, {"id": "#initial_p2tr", "type": "SingletonBeacon", "serviceEndpoint": "bitcoin:bcrt1phpuvck53vp3zad5sjxxep29f8a7p2clfef9t65munnqlqul9qdgqpcr2ev"}]}


    external_genesis_bytes = sha256(jcs.canonicalize(external_document))


    identifier = encode_identifier("external", 1, "testnet4", external_genesis_bytes)

    print("external DID", identifier)
    print("genesis", external_genesis_bytes.hex())

    # print(identifier)

    # decode_identifier(identifier)

    # did_btc1 = "did:btc1:k1qqpuwwde82nennsavvf0lqfnlvx7frrgzs57lchr02q8mz49qzaaxmqphnvcx"

    # id_type, version, network, genesis_bytes = decode_identifier(identifier)

    # print("id type", id_type)
    # print("version", version)
    # print("network", network)



if __name__ == "__main__":
    main()