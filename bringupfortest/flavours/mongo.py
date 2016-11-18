from bringupfortest._builder import DockerControllerBuilder

_start_detector = lambda log_line: "waiting for connections on port" in log_line
_repository = "mongo"
_ports = [27017]


Mongo3DockerController = DockerControllerBuilder(
    name="Mongo3DockerController",
    repository=_repository,
    tag="3",
    started_detection=_start_detector,
    ports=_ports).build()   # type: type

MongoLatestDockerController = DockerControllerBuilder(
    name="MongoLatestDockerController",
    repository=_repository,
    tag="latest",
    started_detection=_start_detector,
    ports=_ports).build()   # type: type

MongoDockerController = MongoLatestDockerController
