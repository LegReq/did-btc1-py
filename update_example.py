from libbtc1.did_manager import DIDManager
from libbtc1.diddoc.builder import Btc1ServiceBuilder
from buidl.ecc import S256Point, PrivateKey, N
import secrets
import jcs
import json
from buidl.helper import big_endian_to_int, sha256
import asyncio

async def create_and_update_did():

    secret = big_endian_to_int(secrets.token_bytes(32)) % N

    private_key = PrivateKey(secret)

    pub_key = private_key.point
    rpc_endpoint = "http://localhost:18443"
    did_manager = DIDManager(rpc_endpoint=rpc_endpoint, rpcuser="polaruser", rpcpassword="polarpass")

    network = "regtest"
    did, did_document = did_manager.create_deterministic(pub_key, network)

    print("Initial Document\n")
    print(json.dumps(did_document.serialize(), indent=2))

    updater = did_manager.updater()

    beacon_secret = big_endian_to_int(secrets.token_bytes(32)) % N

    beacon_sk = PrivateKey(beacon_secret)

    address = beacon_sk.point.p2tr_address(network=network)

    service_builder = Btc1ServiceBuilder(did)

    service = service_builder.add_singleton_beacon(address)

    updater.add_service(service)

    vm_id = did_document.verification_method[0].id



    beacon_id = did_document.service[1].id

    updated_doc = await did_manager.finalize_update_payload(updater, vm_id, private_key, beacon_id, private_key)


    print("\nv2 DID Doc \n")
    print(json.dumps(updated_doc.serialize(), indent=2))

    # TODO: Need better integration with updater and manager
    # Manager should know latest did document.
    # did_manager.announce_update(beacon_id, private_key)


asyncio.run(create_and_update_did())