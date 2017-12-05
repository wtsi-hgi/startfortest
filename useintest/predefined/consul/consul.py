from useintest._common import MissingOptionalPackageError
from useintest.services._builders import DockerisedServiceControllerTypeBuilder
from useintest.services.models import DockerisedService

DEFAULT_HTTP_PORT = 8500

_repository = "consul"
_ports = [8300, 8301, 8302, DEFAULT_HTTP_PORT, 8600]
_start_detector = lambda log_line: "Node info in sync" in log_line or "Synced node info" in log_line


class ConsulDockerisedService(DockerisedService):
    """
    Consul service.
    """
    def create_consul_client(self):
        """
        Gets a client for the Consul service.

        Requires consul (not installed with useintest)
        :return: the consul client
        """
        try:
            from consul import Consul
        except ImportError as e:
            raise MissingOptionalPackageError(e, "python-consul") from e
        return Consul(self.host, self.ports[DEFAULT_HTTP_PORT])


common_setup = {
    "repository": _repository,
    "start_detector": _start_detector,
    "ports": _ports,
    "service_model": ConsulDockerisedService
}

Consul1_0_0ServiceController = DockerisedServiceControllerTypeBuilder(
    name="Consul1_0_0ServiceController",
    tag="1.0.0",
    **common_setup).build()

Consul0_8_4ServiceController = DockerisedServiceControllerTypeBuilder(
    name="Consul0_8_4ServiceController",
    tag="0.8.4",
    **common_setup).build()


ConsulServiceController = Consul1_0_0ServiceController

consul_service_controllers = {Consul1_0_0ServiceController, Consul0_8_4ServiceController}
