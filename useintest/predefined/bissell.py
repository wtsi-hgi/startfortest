from useintest.services._builders import DockerisedServiceControllerTypeBuilder

common_setup = {
    "repository": "mercury/bissell",
    "startup_monitor": lambda service: True,
    "ports": [5000]
}

LatestBissellDockerisedServiceController = DockerisedServiceControllerTypeBuilder(
    name="BissellDockerController",
    tag="latest",
    **common_setup).build()   # type: type

BissellServiceController = LatestBissellDockerisedServiceController

bissell_service_controllers = {BissellServiceController}
