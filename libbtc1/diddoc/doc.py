from pydid.doc.doc import DIDDocument, PossibleServiceTypes
from pydid.did import DID, DIDUrl
from ..service import ServiceBeaconTypes, SingletonBeaconService, SMTAggregateBeaconService, CIDAggregateBeaconService, BeaconTypeNames
from ..did import PLACEHOLDER_DID
from buidl.helper import sha256
import jcs
from typing import Any, List, Optional, Union, Annotated
from pydantic import Field

Btc1PossibleServiceTypes = Union[PossibleServiceTypes, ServiceBeaconTypes]

class Btc1Document(DIDDocument):
    context: Annotated[List[Union[str, dict]], Field(alias="@context")] = [
        "https://www.w3.org/TR/did-1.1", 
        "https://did-btc1/TBD/context"
    ]
    service: Optional[List[Btc1PossibleServiceTypes]] = None


    def canonicalize(self):
        return sha256(jcs.canonicalize(self.serialize()))
        

    def beacon_services(self):
        return [service for service in self.service if service.type in BeaconTypeNames]
    

    # service: Optional[List[ServiceBeaconTypes]] = None

    # @classmethod
    # def deserialize(cls, value: dict) -> "Btc1Document":
    #     """Wrap deserialization with a basic validation pass before matching to type."""
    #     DIDDocument.deserialize(value)
    #     return super(Btc1Document, cls).deserialize(value)
    

    @classmethod
    def deserialize(cls, value: dict) -> "Btc1Document":
        # Make a copy to avoid modifying the input
        value_copy = value.copy()
        
        # Convert services before base validation
        if value_copy.get("service"):
            services = []
            for service in value_copy["service"]:
                if service["type"] == "SingletonBeacon":
                    services.append(SingletonBeaconService(**service))
                elif service["type"] == "SMTAggregateBeacon":
                    services.append(SMTAggregateBeaconService(**service))
                elif service["type"] == "CIDAggregateBeacon":
                    services.append(CIDAggregateBeaconService(**service))
                else:
                    services.append(service)
            value_copy["service"] = services

        DIDDocument.deserialize(value_copy)
        return super().deserialize(value_copy)
    


class IntermediateBtc1DIDDocument(Btc1Document):

    id: DID = PLACEHOLDER_DID

    def to_did_document(self, did: DID) -> Btc1Document:
        did_document = Btc1Document.deserialize(self.model_copy(deep=True).serialize())

        did_document.id = did

        if did_document.controller: 
            for index, controller in enumerate(did_document.controller):
                if controller == PLACEHOLDER_DID:
                    did_document.controller[index] = did

        if did_document.verification_method:
            for index, vm in enumerate(did_document.verification_method):
                if PLACEHOLDER_DID in vm.id:
                    vm.id = DIDUrl.unparse(did, vm.id.path, vm.id.query, vm.id.fragment)
                if vm.controller == PLACEHOLDER_DID:
                    vm.controller = did

        if did_document.authentication:
            for index, vm in enumerate(did_document.authentication):
                if isinstance(vm, DIDUrl) and PLACEHOLDER_DID in vm:
                    did_document.authentication[index] = DIDUrl.unparse(did, vm.path, vm.query, vm.fragment)

                else:
                    if PLACEHOLDER_DID in vm.id:
                        vm.id = DIDUrl.unparse(did, vm.id.path, vm.id.query, vm.id.fragment)
                    if vm.controller == PLACEHOLDER_DID:
                        vm.controller = did

        if did_document.assertion_method:
            for index, vm in enumerate(did_document.assertion_method):
                if isinstance(vm, str) and PLACEHOLDER_DID in vm:
                    did_document.assertion_method[index] = DIDUrl.unparse(did, vm.path, vm.query, vm.fragment)

                else:
                    if PLACEHOLDER_DID in vm.id:
                        vm.id = DIDUrl.unparse(did, vm.id.path, vm.id.query, vm.id.fragment)
                    if vm.controller == PLACEHOLDER_DID:
                        vm.controller = did

        if did_document.capability_delegation:
            for index, vm in enumerate(did_document.capability_delegation):
                if isinstance(vm, DIDUrl) and PLACEHOLDER_DID in vm:
                    did_document.capability_delegation[index] = DIDUrl.unparse(did, vm.path, vm.query, vm.fragment)

                else:
                    if PLACEHOLDER_DID in vm.id:
                        vm.id = DIDUrl.unparse(did, vm.id.path, vm.id.query, vm.id.fragment)
                    if vm.controller == PLACEHOLDER_DID:
                        vm.controller = did

        if did_document.capability_invocation:
            for index, vm in enumerate(did_document.capability_invocation):
                if isinstance(vm, DIDUrl) and PLACEHOLDER_DID in vm:
                    did_document.capability_invocation[index] = DIDUrl.unparse(did, vm.path, vm.query, vm.fragment)

                else:
                    if PLACEHOLDER_DID in vm.id:
                        vm.id = DIDUrl.unparse(did, vm.id.path, vm.id.query, vm.id.fragment)
                    if vm.controller == PLACEHOLDER_DID:
                        vm.controller = did

        if did_document.key_agreement:
            for index, vm in enumerate(did_document.key_agreement):
                if isinstance(vm, DIDUrl) and PLACEHOLDER_DID in vm:
                    did_document.key_agreement[index] = DIDUrl.unparse(did, vm.path, vm.query, vm.fragment)

                else:
                    if PLACEHOLDER_DID in vm.id:
                        vm.id = DIDUrl.unparse(did, vm.id.path, vm.id.query, vm.id.fragment)
                    if vm.controller == PLACEHOLDER_DID:
                        vm.controller = did
        
        if did_document.service:

            for index, service in enumerate(did_document.service):
                if PLACEHOLDER_DID in service.id:
                    
                    did_document.service[index].id = DIDUrl.unparse(did, service.id.path, service.id.query, service.id.fragment)
                  
        return did_document
       
    @staticmethod
    def from_did_document(did_document):
        intermediate_doc: IntermediateBtc1DIDDocument = did_document.model_copy(deep=True)

        did = did_document.id
        intermediate_doc.id = PLACEHOLDER_DID

        if intermediate_doc.controller: 
            for index, controller in enumerate(intermediate_doc.controller):
                if controller == did:
                    intermediate_doc.controller[index] = PLACEHOLDER_DID

        if intermediate_doc.verification_method:
            for index, vm in enumerate(intermediate_doc.verification_method):
                if did in vm.id:
                    vm.id = DIDUrl.unparse(PLACEHOLDER_DID, vm.id.path, vm.id.query, vm.id.fragment)
                if vm.controller == did:
                    vm.controller = PLACEHOLDER_DID

        if intermediate_doc.authentication:
            for index, vm in enumerate(intermediate_doc.authentication):
                if isinstance(vm, DIDUrl) and did in vm:
                    intermediate_doc.authentication[index] = DIDUrl.unparse(PLACEHOLDER_DID, vm.path, vm.query, vm.fragment)

                else:
                    if did in vm.id:
                        vm.id = DIDUrl.unparse(PLACEHOLDER_DID, vm.id.path, vm.id.query, vm.id.fragment)
                    if vm.controller == did:
                        vm.controller = PLACEHOLDER_DID

        if intermediate_doc.assertion_method:
            for index, vm in enumerate(intermediate_doc.assertion_method):
                if isinstance(vm, DIDUrl) and did in vm:
                    intermediate_doc.assertion_method[index] = DIDUrl.unparse(PLACEHOLDER_DID, vm.path, vm.query, vm.fragment)

                else:
                    if did in vm.id:
                        vm.id = DIDUrl.unparse(PLACEHOLDER_DID, vm.id.path, vm.id.query, vm.id.fragment)
                    if vm.controller == did:
                        vm.controller = PLACEHOLDER_DID

        if intermediate_doc.capability_delegation:
            for index, vm in enumerate(intermediate_doc.capability_delegation):
                if isinstance(vm, DIDUrl) and did in vm:
                    intermediate_doc.capability_delegation[index] = DIDUrl.unparse(PLACEHOLDER_DID, vm.path, vm.query, vm.fragment)

                else:
                    if did in vm.id:
                        vm.id = DIDUrl.unparse(PLACEHOLDER_DID, vm.id.path, vm.id.query, vm.id.fragment)
                    if vm.controller == did:
                        vm.controller = PLACEHOLDER_DID

        if intermediate_doc.capability_invocation:
            for index, vm in enumerate(intermediate_doc.capability_invocation):
                if isinstance(vm, DIDUrl) and did in vm:
                    intermediate_doc.capability_invocation[index] = DIDUrl.unparse(PLACEHOLDER_DID, vm.path, vm.query, vm.fragment)

                else:
                    if did in vm.id:
                        vm.id = DIDUrl.unparse(PLACEHOLDER_DID, vm.id.path, vm.id.query, vm.id.fragment)
                    if vm.controller == did:
                        vm.controller = PLACEHOLDER_DID

        if intermediate_doc.key_agreement:
            for index, vm in enumerate(intermediate_doc.key_agreement):
                if isinstance(vm, DIDUrl) and did in vm:
                    intermediate_doc.key_agreement[index] = DIDUrl.unparse(PLACEHOLDER_DID, vm.path, vm.query, vm.fragment)
                else:
                    if did in vm.id:
                        vm.id = DIDUrl.unparse(PLACEHOLDER_DID, vm.id.path, vm.id.query, vm.id.fragment)
                    if vm.controller == did:
                        vm.controller = PLACEHOLDER_DID
        
        if intermediate_doc.service:
            for index, service in enumerate(intermediate_doc.service):
                if did in service.id:
                    intermediate_doc.service[index].id = DIDUrl.unparse(PLACEHOLDER_DID, service.id.path, service.id.query, service.id.fragment)



        return intermediate_doc

