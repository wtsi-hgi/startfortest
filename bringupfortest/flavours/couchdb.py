from copy import copy

from bringupfortest._builder import DockerControllerBuilder

_repository = "couchdb"
_ports = [5984]
_start_detector = lambda log_line: "Apache CouchDB has started" in log_line

_common_setup = {
    "repository": _repository,
    "start_detector": _start_detector,
    "ports": _ports
}

CouchDB1_6Controller = DockerControllerBuilder(
    name="CouchDB1_6Controller",
    tag="1.6",
    **_common_setup).build()   # type: type

CouchDBLatestDockerController = DockerControllerBuilder(
    name="CouchDBLatestDockerController",
    tag="latest",
    **_common_setup).build()   # type: type

CouchDBDockerController = copy(CouchDBLatestDockerController)
