from typing import Set, Optional, Generic, TypeVar

from bidict import bidict
from docker.errors import NotFound
from docker.models.containers import Container

from useintest.common import UseInTestModel, docker_client
from useintest.services.exceptions import UnexpectedNumberOfPortsError

UserType = TypeVar("UserType", bound="User")


class Service(UseInTestModel):
    """
    Model of a service.
    """
    def __init__(self):
        """
        Constructor.
        """
        super().__init__()
        # FIXME: Assumption about where the Docker machine is accessible (i.e. it could be on a VM)
        self.host = "localhost"
        self.ports = bidict()

    @property
    def port(self) -> int:
        """
        Gets the port on the localhost. If there is more than one port exposed, an
        `UnexpectedNumberOfPortsException` will be raised.
        :return: the exposed port
        """
        if len(self.ports) != 1:
            raise UnexpectedNumberOfPortsError("%d ports are exposed (cannot use `port`)" % len(self.ports))
        return list(self.ports.values())[0]

    def get_external_port_mapping_to(self, port: int) -> int:
        """
        Gets the port on localhost to which the given port in the container maps to.
        :param port: the port inside the container
        :return: the port outside that maps to that in the container
        """
        return self.ports.inv[port]


class DockerisedService(Service):
    """
    Model of a service running in a Docker container.
    """
    @property
    def container(self) -> Optional[Container]:
        if self.container_id is None:
            return None
        try:
            return docker_client.containers.get(self.container_id)
        except NotFound:
            return None

    @container.setter
    def container(self, container: Container):
        self.container_id = container.id

    @property
    def container_id(self) -> Optional[str]:
        return self._container_id

    @container_id.setter
    def container_id(self, container_id: str):
        self._container_id = container_id

    def __init__(self):
        super().__init__()
        self.name = None
        self._container_id: str = None
        self.controller = None

    # TODO: Not sure of the best way to specify the type as it could be that of a subclass...
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.controller.stop_service(self)


class User(UseInTestModel):
    """
    A user with an associated password.
    """
    def __init__(self, username: str, password: str=None):
        self.username = username
        self.password = password

    def __eq__(self, other) -> bool:
        return type(other) == type(self) \
               and other.username == self.username \
               and other.password == self.password

    def __hash__(self) -> hash:
        return hash(self.username + self.password)


class ServiceWithUsers(Generic[UserType], Service):
    """
    A service with users.
    """
    def __init__(self):
        super().__init__()
        self.users: Set[UserType] = set()
        self._root_user: Optional[UserType] = None

    @property
    def root_user(self) -> Optional[UserType]:
        """
        Gets a user of the service that has privileged access. 
        :return: a user with privilege access
        """
        assert self._root_user in self.users
        return self._root_user

    @root_user.setter
    def root_user(self, user: Optional[UserType]):
        """
        Sets the user of the service that has privileged access.
        :param user: the user with privilege access
        """
        if user is not None and not user in self.users:
            self.users.add(user)
        self._root_user = user


class DockerisedServiceWithUsers(Generic[UserType], DockerisedService, ServiceWithUsers[UserType]):
    """
    Service running on Docker with users.
    """
