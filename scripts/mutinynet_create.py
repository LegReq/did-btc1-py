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
    network = "mutinynet"
    btc_network = "signet"

    # mnemonic = "prosper can dial lumber write coconut express imitate husband isolate inside release brush media please kind comic pill science repeat basic also endorse bronze"
    root_hdpriv = HDPrivateKey.from_mnemonic(mnemonic, network=btc_network)
    print("Mnemonic : ", mnemonic)
    
    initial_sk = root_hdpriv.get_private_key(didkey_purpose, address_num=0)
    initial_pk = initial_sk.point

    print("Secp256k1 PrivateKey", initial_sk.hex())
    print("Secp256k1 Public Key", initial_pk.sec())
    
        

    did_manager = DIDManager(did_network=network, btc_network=btc_network, esplora_base="https://mutinynet.com/api")
    
    identifier, did_doc = await did_manager.create_deterministic(initial_sk, network)

    print(identifier)
    print(json.dumps(did_doc.serialize(), indent=2))


    



asyncio.run(generate_deterministic_test_vector())