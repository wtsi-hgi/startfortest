from useintest.services._builders import DockerisedServiceControllerTypeBuilder

_repository = "consul"
_ports = [8300, 8301, 8302, 8500, 8600]
_start_detector = lambda log_line: "consul: New leader elected" in log_line


common_setup = {
    "repository": _repository,
    "start_detector": _start_detector,
    "ports": _ports,
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
