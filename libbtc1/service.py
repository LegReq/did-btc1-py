from pydid.service import Service
from typing_extensions import Literal


class SingletonBeaconService(Service):
    type: Literal["SingletonBeacon"]


class SMTAggregateBeaconService(Service):
    type: Literal["SMTAggregate"]


class CIDAggregateBeaconService(Service):
    type: Literal["CIDAggregate"]