from pydid.doc.builder import ServiceBuilder, DIDDocumentBuilder
from pydid.did import DID

from ..service import SingletonBeaconService
from typing import Iterator, List, Optional, Type, Union


class Btc1ServiceBuilder(ServiceBuilder):

    def add_singleton_beacon(self, ident, beacon_address):
        ident = ident or next(self._id_generator)

        service_endpoint = f"bitcoin:{beacon_address}"
        service = SingletonBeaconService.make(
            id=self._did.ref(ident),
            service_endpoint=service_endpoint    
        )

        self.services.append(service)
        return service
    

class Btc1DIDDocumentBuilder(DIDDocumentBuilder):

    def __init__(
        self,
        id: Union[str, DID],
        context: List[str] = None,
        *,
        also_known_as: List[str] = None,
        controller: Union[List[str], List[DID]] = None,
    ):
        super().__init__(id=id, context=context, also_known_as=also_known_as, controller=controller)
        self.service = Btc1ServiceBuilder(self.id)

    #     @classmethod
    # def from_doc(cls, doc: DIDDocument) -> "DIDDocumentBuilder":
    #     """Create a Builder from an existing DIDDocument."""
    #     builder = cls(
    #         id=doc.id,
    #         context=doc.context,
    #         also_known_as=doc.also_known_as,
    #         controller=doc.controller,
    #     )
    #     builder.verification_method = VerificationMethodBuilder(
    #         doc.id, methods=doc.verification_method
    #     )
    #     builder.authentication = RelationshipBuilder(
    #         doc.id, "auth", methods=doc.authentication
    #     )
    #     builder.assertion_method = RelationshipBuilder(
    #         doc.id, "assert", methods=doc.assertion_method
    #     )
    #     builder.key_agreement = RelationshipBuilder(
    #         doc.id, "key-agreement", methods=doc.key_agreement
    #     )
    #     builder.capability_invocation = RelationshipBuilder(
    #         doc.id, "capability-invocation", methods=doc.capability_invocation
    #     )
    #     builder.capability_delegation = RelationshipBuilder(
    #         doc.id, "capability-delegation", methods=doc.capability_delegation
    #     )
    #     builder.service = Btc1ServiceBuilder(doc.id, services=doc.service)
    #     return builder