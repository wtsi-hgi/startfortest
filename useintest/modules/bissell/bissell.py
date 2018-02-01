from time import sleep

import requests

from useintest.services.builders import DockerisedServiceControllerTypeBuilder
from useintest.services.exceptions import TransientServiceStartError
from useintest.services.models import DockerisedService


def startup_monitor(service: DockerisedService):
    """
    Checks whether Bissell has started.

    Discussion on how to do this can be found here: https://github.com/wtsi-hgi/bissell/issues/1.
    :param service: the Bissell service
    :return: `True`
    """
    while True:
        logs = service.container.logs()
        if len(logs) > 0:
            TransientServiceStartError(f"Bissell output detected in logs indicates a startup failure: {logs}")
        try:
            response = requests.head(f"http://{service.host}:{service.port}")
            if response.status_code == 401:
                return True
        except requests.exceptions.ConnectionError:
            pass
        sleep(10)


common_setup = {
    "repository": "mercury/bissell",
    "startup_monitor": startup_monitor,
    "ports": [5000]
}

LatestBissellDockerisedServiceController = DockerisedServiceControllerTypeBuilder(
    name="BissellDockerController",
    tag="latest",
    **common_setup).build()   # type: type

BissellServiceController = LatestBissellDockerisedServiceController

bissell_service_controllers = {BissellServiceController}
