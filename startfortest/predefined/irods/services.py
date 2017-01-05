from abc import ABCMeta
from typing import Type

from hgicommon.helpers import get_open_port
from startfortest.services.controllers import ServiceController
from startfortest.services.models import DockerisedService
from testwithirods.api import IrodsVersion, get_static_irods_server_controller
from testwithirods.models import ContainerisedIrodsServer


class IrodsDockerisedService(ContainerisedIrodsServer, DockerisedService):
    """
    Combination model of a Dockerised iRODS service, compatible with both this library and `test-with-irods`.
    """
    def __init__(self):
        super().__init__()

    @property
    def container(self) -> dict:
        return self.native_object

    @container.setter
    def container(self, value: dict):
        self.native_object = value

    @DockerisedService.port.setter
    def port(self, value: int):
        if value is not None:
            self.ports[value] = value


class IrodsServiceController(ServiceController, metaclass=ABCMeta):
    """
    iRODS service controller.
    """
    def __init__(self, irods_version: IrodsVersion):
        """
        TODO
        :param irods_version:
        """
        super().__init__(IrodsDockerisedService)
        self.irods_server_controller = get_static_irods_server_controller(irods_version=irods_version)

    def __del__(self):
        try:
            self.irods_server_controller.tear_down()
        except AttributeError:
            """ Constructor not completed """

    def start_service(self) -> IrodsDockerisedService:
        mapped_port = get_open_port()
        test_with_irods_server = self.irods_server_controller.start_server(mapped_port)
        service = IrodsDockerisedService()
        # Rather hacky model conversion
        for property, value in vars(test_with_irods_server).items():
            setattr(service, property, value)
        service.ports[1247] = mapped_port
        return service

    def stop_service(self, service: IrodsDockerisedService):
        self.irods_server_controller.stop_server(service)


def _build_irods_service_controller_type(irods_version: IrodsVersion) -> Type[IrodsServiceController]:
    """
    Builds an iRODS service controller type for the version of iRODs given.
    :param irods_version: version of iRODS that the controller is for
    :return: the build controller type
    """
    def init(self: IrodsServiceController):
        super(type(self), self).__init__(irods_version)

    return type(
        "Irods%sController" % irods_version.name.replace("v", ""),
        (IrodsServiceController,),
        {"__init__": init}
    )


Irods4_1_10Controller = _build_irods_service_controller_type(IrodsVersion.v4_1_10)
IrodsController = Irods4_1_10Controller