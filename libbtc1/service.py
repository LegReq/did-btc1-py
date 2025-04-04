from pydid.service import Service
from typing_extensions import Literal


SINGLETON_BEACON = Literal["SingletonBeacon"]
SMT_AGGREGATE_BEACON = Literal["SMTAggregateBeacon"]
CID_AGGREGATE_BEACON = Literal["CIDAggregateBeacon"]

BeaconTypes = [SINGLETON_BEACON, SMT_AGGREGATE_BEACON, CID_AGGREGATE_BEACON]


class SingletonBeaconService(Service):
    type: SINGLETON_BEACON


class SMTAggregateBeaconService(Service):
    type: SMT_AGGREGATE_BEACON


class CIDAggregateBeaconService(Service):
    type: CID_AGGREGATE_BEACON