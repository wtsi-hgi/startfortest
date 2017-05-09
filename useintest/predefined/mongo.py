from useintest.services._builders import DockerisedServiceControllerTypeBuilder

common_setup = {
    "repository": "mongo",
    "start_detector": lambda log_line: "waiting for connections on port" in log_line,
    "persistent_error_detector": lambda log_line: "error creating journal dir" in log_line
                                                  or "No space left on device" in log_line,
    "ports": [27017]
}

Mongo3DockerisedServiceController = DockerisedServiceControllerTypeBuilder(
    name="Mongo3DockerController",
    tag="3",
    **common_setup).build()   # type: type

MongoLatestDockerisedServiceController = DockerisedServiceControllerTypeBuilder(
    name="MongoLatestDockerController",
    tag="latest",
    **common_setup).build()   # type: type


Mongo3ServiceController = Mongo3DockerisedServiceController
MongoServiceController = MongoLatestDockerisedServiceController

mongo_service_controllers = {Mongo3ServiceController, MongoServiceController}