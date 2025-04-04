
from .did import encode_identifier, KEY, EXTERNAL, NETWORKS, VERSIONS
from .resolver import resolve
import jcs
from buidl.helper import sha256
from pydid.doc import DIDDocument
from .did import PLACEHOLDER_DID
from .diddoc.doc import IntermediateBtc1DIDDocument
from .diddoc.builder import Btc1DIDDocumentBuilder

def create_deterministic(public_key, network="bitcoin", version=1):
    if network not in NETWORKS:
        raise Exception(f"Invalid Network : {network}")
    
    if version not in VERSIONS:
        raise Exception(f"Invalid Version : {version}")
    
    builder = Btc1DIDDocumentBuilder.from_secp256k1_key(public_key, network, version)

    did_document = builder.build()


    return did_document.id, did_document

def create_external(intermediate_document: IntermediateBtc1DIDDocument, network = "bitcoin", version = 1):
    if network not in NETWORKS:
        raise Exception(f"Invalid Network : {network}")
    
    if version not in VERSIONS:
        raise Exception(f"Invalid Version : {version}")
    
    if intermediate_document.id != PLACEHOLDER_DID:
        raise Exception(f"Intermediate Document must use placeholder id : {intermediate_document.id}")
    

    genesis_bytes = sha256(jcs.canonicalize(intermediate_document.serialize()))

    identifier = encode_identifier(EXTERNAL, version, network, genesis_bytes)

    did_document = intermediate_document.to_did_document(identifier)

    # did_document.id = identifier

    # for index, controller in enumerate(did_document.controller):
    #     if controller == PLACEHOLDER_DID:
    #         did_document.controller[index] = identifier


    # for index, vm in enumerate(did_document.verification_method):
    #     print(vm)
    #     if PLACEHOLDER_DID in vm.id:
    #         vm.id = vm.id.replace(PLACEHOLDER_DID, identifier)
    #     if vm.controller == PLACEHOLDER_DID:
    #         vm.controller = vm.controller.replace(PLACEHOLDER_DID, identifier)

    # for index, vm in enumerate(did_document.authentication):
    #     if isinstance(vm, str) and PLACEHOLDER_DID in vm:
    #         did_document.authentication[index] = vm.replace(PLACEHOLDER_DID, identifier)

    #     else:
    #         if PLACEHOLDER_DID in vm.id:
    #             vm.id = vm.id.replace(PLACEHOLDER_DID, identifier)
    #         if vm.controller == PLACEHOLDER_DID:
    #             vm.controller = identifier

    # for index, vm in enumerate(did_document.assertion_method):
    #     if isinstance(vm, str) and PLACEHOLDER_DID in vm:
    #         did_document.authentication[index] = vm.replace(PLACEHOLDER_DID, identifier)

    #     else:
    #         if PLACEHOLDER_DID in vm.id:
    #             vm.id = vm.id.replace(PLACEHOLDER_DID, identifier)
    #         if vm.controller == PLACEHOLDER_DID:
    #             vm.controller = identifier

    # for index, vm in enumerate(did_document.capability_delegation):
    #     if isinstance(vm, str) and PLACEHOLDER_DID in vm:
    #         did_document.authentication[index] = vm.replace(PLACEHOLDER_DID, identifier)

    #     else:
    #         if PLACEHOLDER_DID in vm.id:
    #             vm.id = vm.id.replace(PLACEHOLDER_DID, identifier)
    #         if vm.controller == PLACEHOLDER_DID:
    #             vm.controller = identifier

    # for index, vm in enumerate(did_document.key_agreement):
    #     if isinstance(vm, str) and PLACEHOLDER_DID in vm:
    #         did_document.authentication[index] = vm.replace(PLACEHOLDER_DID, identifier)

    #     else:
    #         if PLACEHOLDER_DID in vm.id:
    #             vm.id = vm.id.replace(PLACEHOLDER_DID, identifier)
    #         if vm.controller == PLACEHOLDER_DID:
    #             vm.controller = identifier

    #             vm.controller = identifier
    
    
    

    return identifier, did_document


    