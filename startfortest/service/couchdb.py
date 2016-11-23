from startfortest._builder import DockerisedServiceControllerTypeBuilder

_repository = "couchdb"
_ports = [5984]
_start_detector = lambda log_line: "Apache CouchDB has started" in log_line

_common_setup = {
    "repository": _repository,
    "start_detector": _start_detector,
    "ports": _ports
}

CouchDB1_6DockerisedServiceController = DockerisedServiceControllerTypeBuilder(
    name="CouchDB1_6Controller",
    tag="1.6",
    **_common_setup).build()   # type: type

CouchDBDockerisedServiceController = DockerisedServiceControllerTypeBuilder(
    name="CouchDBLatestDockerController",
    tag="latest",
    **_common_setup).build()   # type: type


CouchDB1_6Controller = CouchDB1_6DockerisedServiceController
CouchDBController = CouchDBDockerisedServiceController
