from useintest.services._builders import DockerisedServiceControllerTypeBuilder

common_setup = {
    "repository": "mercury/bissell",
    "startup_monitor": lambda log_line: True,
    "ports": [5000]
}

BissellDockerisedServiceController = DockerisedServiceControllerTypeBuilder(
    name="BissellDockerController",
    tag="latest",
    **common_setup).build()   # type: type

BissellServiceController = BissellDockerisedServiceController

bissell_service_controllers = {BissellServiceController}