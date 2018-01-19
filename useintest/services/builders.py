from abc import ABCMeta
from typing import Type, TypeVar

from useintest.services.controllers import DockerisedServiceController, ServiceType, DockerisedServiceType
from useintest.services.models import DockerisedService, Service

DockerControllerType = TypeVar("DockerControllerType", bound=DockerisedServiceController)


class ServiceControllerTypeBuilder(metaclass=ABCMeta):
    """
    Builder for controllers with particular setups (e.g. repositories and tags).
    """
    def __init__(self, name: str, *args, superclass: Type[DockerControllerType],
                 service_model: Type[ServiceType]=Service, **kwargs):
        """
        Constructor.
        :param name: name of the type that is to be created
        :param args: any arguments that are to be automatically given to the superclass constructor
        :param superclass: the superclass of the type that is to be created
        :param service_model: model of the service the controller type controls
        :param kwargs: any named arguments that are to be automatically given to the superclass constructor
        """
        self.name = name
        self.superclass = superclass
        self.service_model = service_model
        self.args = args
        self.kwargs = kwargs

    def build(self) -> Type[DockerControllerType]:
        """
        Builds the new controller type.
        :return: the new controller type
        """
        def init(controller_self, *args, **kwargs):
            super(type(controller_self), controller_self).__init__(
                self.service_model, *self.args, *args, **{**self.kwargs, **kwargs})

        return type(
            self.name,
            (self.superclass[self.service_model], ),
            {"__init__": init}
        )


class DockerisedServiceControllerTypeBuilder(ServiceControllerTypeBuilder):
    """
    Builder for Docker controllers with particular setups (e.g. repositories and tags).
    """
    def __init__(self, name: str, *args, superclass: Type[DockerisedServiceController]=DockerisedServiceController,
                 service_model: Type[DockerisedServiceType]=DockerisedService, **kwargs):
        super().__init__(name, *args, superclass=superclass, service_model=service_model, **kwargs)
