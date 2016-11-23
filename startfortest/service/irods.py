from abc import ABCMeta
from typing import Type

from startfortest.controllers import ServerController
from startfortest.models import DockerisedService
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
        self.ports[1247] = value


class IrodsServiceController(ServerController, metaclass=ABCMeta):
    """
    TOOD
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
        test_with_irods_server = self.irods_server_controller.start_server()
        service = IrodsDockerisedService()
        # Rather hacky model conversion
        for property, value in vars(test_with_irods_server).items():
            setattr(service, property, value)
        return service

    def stop_service(self, service: IrodsDockerisedService):
        self.irods_server_controller.stop_server(service)


def _build_irods_service_controller_type(irods_version: IrodsVersion) -> Type[IrodsServiceController]:
    """
    TODO
    :param irods_version:
    :return:
    """
    def init(self: IrodsServiceController):
        super(type(self), self).__init__(irods_version)

    return type(
        "Irods%sController" % irods_version.name.replace("v", ""),
        (IrodsServiceController,),
        {"__init__": init}
    )


Irods4_1_10Controller = _build_irods_service_controller_type(IrodsVersion.v4_1_10)
