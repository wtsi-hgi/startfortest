from useintest.services.builders import DockerisedServiceControllerTypeBuilder

common_setup = {
    "repository": "mercury/bissell",
    "start_log_detector": lambda line: "Bissell starting on port" in line,
    "start_http_detector": lambda response: response.status_code == 401,
    "ports": [5000]
}

LatestBissellDockerisedServiceController = DockerisedServiceControllerTypeBuilder(
    name="BissellDockerController",
    tag="latest",
    **common_setup).build()   # type: type

BissellServiceController = LatestBissellDockerisedServiceController

bissell_service_controllers = {BissellServiceController}
