from copy import copy

from bringupfortest._builder import DockerControllerBuilder

_repository = "mongo"
_ports = [27017]
_start_detector = lambda log_line: "waiting for connections on port" in log_line
_persistent_error_detector = lambda log_line: "error creating journal dir" in log_line

_common_setup = {
    "repository": _repository,
    "start_detector": _start_detector,
    "persistent_error_detector": _persistent_error_detector,
    "ports": _ports
}

Mongo3DockerController = DockerControllerBuilder(
    name="Mongo3DockerController",
    tag="3",
    **_common_setup).build()   # type: type

MongoLatestDockerController = DockerControllerBuilder(
    name="MongoLatestDockerController",
    tag="latest",
    **_common_setup).build()   # type: type

MongoDockerController = copy(MongoLatestDockerController)
