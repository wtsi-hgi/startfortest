import os

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
    CONSUL_ADDRESS_ENVIRONMENT_VARIABLE = "CONSUL_HTTP_ADDR"
    CONSUL_TOKEN_ENVIRONMENT_VARIABLE = "CONSUL_HTTP_TOKEN"
    CONSUL_SCHEME_ENVIRONMENT_VARIABLE = "CONSUL_SCHEME"
    CONSUL_DATACENTRE_ENVIRONMENT_VARIABLE = "CONSUL_DC"
    CONSUL_VERIFY_ENVIRONMENT_VARIABLE = "CONSUL_HTTP_SSL_VERIFY"
    CONSUL_CERTIFICATE_ENVIRONMENT_VARIABLE = "CONSUL_CLIENT_CERT"

    @staticmethod
    def _clear_environment():
        """
        Clears the environment variables related to Consul.
        """
        os.environ.pop(ConsulDockerisedService.CONSUL_ADDRESS_ENVIRONMENT_VARIABLE, None)
        os.environ.pop(ConsulDockerisedService.CONSUL_TOKEN_ENVIRONMENT_VARIABLE, None)
        os.environ.pop(ConsulDockerisedService.CONSUL_SCHEME_ENVIRONMENT_VARIABLE, None)
        os.environ.pop(ConsulDockerisedService.CONSUL_DATACENTRE_ENVIRONMENT_VARIABLE, None)
        os.environ.pop(ConsulDockerisedService.CONSUL_VERIFY_ENVIRONMENT_VARIABLE, None)
        os.environ.pop(ConsulDockerisedService.CONSUL_CERTIFICATE_ENVIRONMENT_VARIABLE, None)

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
        ConsulDockerisedService._clear_environment()
        return Consul(self.host, self.ports[DEFAULT_HTTP_PORT])

    def setup_environment(self):
        """
        Sets Consul related environment variables.
        """
        ConsulDockerisedService._clear_environment()
        os.environ[ConsulDockerisedService.CONSUL_ADDRESS_ENVIRONMENT_VARIABLE] = \
            f"{self.host}:{self.ports[DEFAULT_HTTP_PORT]}"


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
