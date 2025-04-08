from pydid.doc import DIDDocument
from pydid.did import DID
from ..did import PLACEHOLDER_DID

# class Btc1Document(DIDDocument):

#     def from_secp256k1_key():

        


class IntermediateBtc1DIDDocument(DIDDocument):

    id: DID = PLACEHOLDER_DID

    def to_did_document(self, did: DID) -> DIDDocument:
        did_document: DIDDocument = self.model_copy()

        did_document.id = did

        if did_document.controller: 
            for index, controller in enumerate(did_document.controller):
                if controller == PLACEHOLDER_DID:
                    self.controller[index] = did

        if did_document.verification_method:
            for index, vm in enumerate(did_document.verification_method):
                print(vm)
                if PLACEHOLDER_DID in vm.id:
                    vm.id = vm.id.replace(PLACEHOLDER_DID, did)
                if vm.controller == PLACEHOLDER_DID:
                    vm.controller = vm.controller.replace(PLACEHOLDER_DID, did)

        if did_document.authentication:
            for index, vm in enumerate(did_document.authentication):
                if isinstance(vm, str) and PLACEHOLDER_DID in vm:
                    did_document.authentication[index] = vm.replace(PLACEHOLDER_DID, did)

                else:
                    if PLACEHOLDER_DID in vm.id:
                        vm.id = vm.id.replace(PLACEHOLDER_DID, did)
                    if vm.controller == PLACEHOLDER_DID:
                        vm.controller = did

        if did_document.assertion_method:
            for index, vm in enumerate(did_document.assertion_method):
                if isinstance(vm, str) and PLACEHOLDER_DID in vm:
                    did_document.authentication[index] = vm.replace(PLACEHOLDER_DID, did)

                else:
                    if PLACEHOLDER_DID in vm.id:
                        vm.id = vm.id.replace(PLACEHOLDER_DID, did)
                    if vm.controller == PLACEHOLDER_DID:
                        vm.controller = did

        if did_document.capability_delegation:
            for index, vm in enumerate(did_document.capability_delegation):
                if isinstance(vm, str) and PLACEHOLDER_DID in vm:
                    did_document.authentication[index] = vm.replace(PLACEHOLDER_DID, did)

                else:
                    if PLACEHOLDER_DID in vm.id:
                        vm.id = vm.id.replace(PLACEHOLDER_DID, did)
                    if vm.controller == PLACEHOLDER_DID:
                        vm.controller = did

        if did_document.capability_invocation:
            for index, vm in enumerate(did_document.capability_invocation):
                if isinstance(vm, str) and PLACEHOLDER_DID in vm:
                    did_document.authentication[index] = vm.replace(PLACEHOLDER_DID, did)

                else:
                    if PLACEHOLDER_DID in vm.id:
                        vm.id = vm.id.replace(PLACEHOLDER_DID, did)
                    if vm.controller == PLACEHOLDER_DID:
                        vm.controller = did

        if did_document.key_agreement:
            for index, vm in enumerate(did_document.key_agreement):
                if isinstance(vm, str) and PLACEHOLDER_DID in vm:
                    did_document.authentication[index] = vm.replace(PLACEHOLDER_DID, did)

                else:
                    if PLACEHOLDER_DID in vm.id:
                        vm.id = vm.id.replace(PLACEHOLDER_DID, did)
                    if vm.controller == PLACEHOLDER_DID:
                        vm.controller = did
        
        if did_document.service:
            for index, service in enumerate(did_document.service):
                if PLACEHOLDER_DID in service.id:
                    did_document.service[index].id = service.id.replace(PLACEHOLDER_DID, did)



        return did_document

