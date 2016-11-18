from bringupfortest._builder import DockerControllerBuilder


Mongo3DockerController = DockerControllerBuilder(
    name="Mongo3DockerController",
    repository="mongo",
    tag="3",
    started_detection=lambda log_line: "waiting for connections on port" in log_line,
    exposed_ports=[27017])
