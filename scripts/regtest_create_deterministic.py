from buidl.mnemonic import secure_mnemonic
from buidl.hd import HDPrivateKey
from pydid.verification_method import Multikey
from pydid.doc.builder import VerificationMethodBuilder
from pydid.did import DIDUrl
import json
import asyncio
from libbtc1.did import encode_identifier, decode_identifier, PLACEHOLDER_DID
from libbtc1.resolver import Btc1Resolver
from libbtc1.service import SingletonBeaconService
from libbtc1.diddoc.builder import Btc1DIDDocumentBuilder, IntermediateBtc1DIDDocumentBuilder
from libbtc1.multikey import get_public_key_multibase
import os
from libbtc1.did_manager import DIDManager
from libbtc1.beacon_manager import BeaconManager
from libbtc1.diddoc.builder import Btc1ServiceBuilder
import time
from bitcoinrpc import BitcoinRPC
from buidl.tx import Tx
from libbtc1.helpers import fund_regtest_beacon_address

async def generate_deterministic_test_vector():

    didkey_purpose = "11"
    ## Run this if you want a new hardware key
    mnemonic = secure_mnemonic()
    network = "regtest"

    # mnemonic = "prosper can dial lumber write coconut express imitate husband isolate inside release brush media please kind comic pill science repeat basic also endorse bronze"
    root_hdpriv = HDPrivateKey.from_mnemonic(mnemonic, network=network)
    print("Mnemonic : ", mnemonic)
    
    initial_sk = root_hdpriv.get_private_key(didkey_purpose, address_num=0)
    initial_pk = initial_sk.point

    print("Secp256k1 PrivateKey", initial_sk.hex())
    print("Secp256k1 Public Key", initial_pk.sec())
    
    # pk_multibase = get_public_key_multibase(initial_pk.sec())

    # vm = builder.verification_method.add(Multikey, controller=PLACEHOLDER_DID, public_key_multibase = pk_multibase)

    # builder.authentication.reference(vm.id)

    # # builder.authentication.add(Multikey, public_key_multibase=pk_multibase)
    
    # cap_sk = root_hdpriv.get_private_key(didkey_purpose, address_num=1)
    # cap_pk = cap_sk.point

    # print("Secp256k1 PrivateKey", cap_sk.hex())
    # print("Secp256k1 Public Key", cap_pk.sec())
    

    
    # pk_multibase = get_public_key_multibase(cap_pk.sec())

    # cap_vm = builder.verification_method.add(Multikey, controller=PLACEHOLDER_DID, public_key_multibase=pk_multibase)
    
    keys = {
        "genesisKey": {
            "pk": initial_pk.sec().hex(),
            "sk": initial_sk.hex()
        },

    }
        
    
    # beacon_sk = root_hdpriv.get_private_key(didkey_purpose, address_num=2)
    # beacon_pk = beacon_sk.point
    
    # address = beacon_pk.p2wpkh_address(network="regtest")

    # beacon_service = builder.service.add_singleton_beacon(beacon_address=address)


    rpc_endpoint = "http://localhost:18443"

    bitcoin_rpc = BitcoinRPC.from_config(rpc_endpoint, ("polaruser", "polarpass"))

    did_manager = DIDManager(network=network)
    
    identifier, did_doc = await did_manager.create_deterministic(initial_sk, network)
    for beacon_id, beacon_manager in did_manager.beacon_managers.items():
        await fund_regtest_beacon_address(bitcoin_rpc, beacon_manager)
    
    print(json.dumps(did_doc.serialize(), indent=2))

    did_path = identifier.split(":")[2]
    
    folder_path = f"TestVectors/{network}/{did_path}"

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        

    
    did_path = f"{folder_path}/did.txt"
    
    with open(did_path, "w") as f:
        f.write(identifier)
    
    
    initial_path = f"{folder_path}/initialDidDoc.json"
    
    with open(initial_path, "w") as f:
        json.dump(did_doc.serialize(), f, indent=2)
        
    
    updater = did_manager.updater()


    new_beacon_sk = root_hdpriv.get_private_key(didkey_purpose, address_num=2)

    beacon_script = new_beacon_sk.point.p2wpkh_script()
    address = beacon_script.address(network=network)

    service_builder = Btc1ServiceBuilder(identifier, services=did_doc.service)

    new_beacon_service = service_builder.add_singleton_beacon(address)

    updater.add_service(new_beacon_service)

    beacon_manager = did_manager.add_beacon_manager(new_beacon_service.id, new_beacon_sk, beacon_script)
    await fund_regtest_beacon_address(bitcoin_rpc, beacon_manager)
    
    
    beacon_id = did_doc.service[1].id

    vm_id = did_doc.verification_method[0].id

    updated_doc = await did_manager.finalize_update_payload(updater, vm_id, initial_sk, beacon_id)
    
    doc_v2 = updated_doc.model_copy(deep=True)
    time.sleep(120)
    
    updater = did_manager.updater()
    
    new_vm_sk = root_hdpriv.get_private_key(didkey_purpose, address_num=3)
    
    new_vm_pk = new_vm_sk.point
    
    new_pk_multibase = get_public_key_multibase(new_vm_pk.sec())

    vm_builder = VerificationMethodBuilder(identifier, methods=updated_doc.verification_method)
    
    new_vm = vm_builder.add(Multikey, public_key_multibase=new_pk_multibase)
    
    updater.add_verification_method(new_vm)
        
    second_updated_doc = await did_manager.finalize_update_payload(updater, vm_id, initial_sk, new_beacon_service.id)

    
    keys[new_beacon_service.id] = {
            "pk": new_beacon_sk.point.sec().hex(),
            "sk": new_beacon_sk.hex()
    }
    keys[new_vm.id] = {
            "pk": new_vm_pk.sec().hex(),
            "sk": new_vm_sk.hex()
    }
    
    
    keys_path = f"{folder_path}/keys.json"
    
    with open(keys_path, "w") as f:
        json.dump(keys, f, indent=2)
        
    
    print("Updated Doc")
    print(json.dumps(second_updated_doc.serialize(), indent=2))
    print("Sidecar data")
    print(json.dumps(did_manager.get_sidecar_data(), indent=2))
    
        
    target_doc_path = f"{folder_path}/didDocumentv2.json"
    
    with open(target_doc_path, "w") as f:
        json.dump(doc_v2.serialize(), f, indent=2)
        
    target_doc_path = f"{folder_path}/targetDidDocument.json"
    
    with open(target_doc_path, "w") as f:
        json.dump(second_updated_doc.serialize(), f, indent=2)
    
    resolution_options = {
        "sidecarData": did_manager.get_sidecar_data()
    }
    
    res_options_path = f"{folder_path}/resolutionOptions.json"
    
    with open(res_options_path, "w") as f:
        json.dump(resolution_options, f, indent=2)
    



asyncio.run(generate_deterministic_test_vector())