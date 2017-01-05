import atexit
import logging
import os
import tempfile
from abc import abstractmethod, ABCMeta
from typing import Sequence, Type

from docker.errors import APIError

from hgicommon.docker.client import create_client
from hgicommon.helpers import create_random_string
from startfortest.predefined.irods.testwithirods import ContainerisedIrodsServer, IrodsServer, IrodsUser, Version


class IrodsServerController(metaclass=ABCMeta):
    """
    Controller for containerised iRODS servers.
    """
    _DOCKER_CLIENT = create_client()
    _DEFAULT_IRODS_PORT = 1247

    @staticmethod
    def _create_container(image_name: str, irods_version: Version, users: Sequence[IrodsUser], mapped_port: int=None) \
            -> ContainerisedIrodsServer:
        """
        Creates a iRODS server container running the given image.
        :param image_name: the image to run
        :param irods_version: version of iRODS
        :param users: the iRODS users
        :param mapped_port: map iRODS port to this port on the Docker host machine
        :return: the containerised iRODS server
        """
        docker_image = IrodsServerController._DOCKER_CLIENT.images(image_name, quiet=True)

        if len(docker_image) == 0:
            docker_image = image_name
            # Note: Unlike with Docker cli, docker-py does not appear to search for images on Docker Hub if they are not
            # found when building
            logging.info("Pulling iRODs server Docker image: %s - this may take a few minutes" % docker_image)
            response = IrodsServerController._DOCKER_CLIENT.pull(docker_image)
            logging.debug(response)
        else:
            docker_image = docker_image[0]

        container_name = create_random_string("irods")
        port_mappings = None if mapped_port is None else {IrodsServerController._DEFAULT_IRODS_PORT: mapped_port}
        logging.info("Creating iRODs server Docker container: %s" % container_name)
        container = IrodsServerController._DOCKER_CLIENT.create_container(
            image=docker_image, name=container_name, ports=[IrodsServerController._DEFAULT_IRODS_PORT],
            host_config=IrodsServerController._DOCKER_CLIENT.create_host_config(port_bindings=port_mappings))

        irods_server = ContainerisedIrodsServer()
        irods_server.native_object = container
        irods_server.name = container_name
        irods_server.host = container_name
        irods_server.version = irods_version
        irods_server.users = users
        irods_server.port = IrodsServerController._DEFAULT_IRODS_PORT
        if mapped_port is not None:
            irods_server.mapped_port = port_mappings[IrodsServerController._DEFAULT_IRODS_PORT]
        return irods_server

    @abstractmethod
    def write_connection_settings(self, file_location: str, irods_server: IrodsServer):
        """
        Writes the connection settings for the given iRODS server to the given location.
        :param file_location: the location to write the settings to (file should not already exist)
        :param irods_server: the iRODS server to create the connection settings for
        """

    @abstractmethod
    def _wait_for_start(self, container: ContainerisedIrodsServer) -> bool:
        """
        Blocks until the given containerized iRODS server has started.
        :param container: the containerised server
        """

    @abstractmethod
    def start_server(self, mapped_port: int=None) -> ContainerisedIrodsServer:
        """
        Starts a containerised iRODS server and blocks until it is ready to be used.
        :param mapped_port: map iRODS's connection port to this port on the machine running docker
        :return: the started containerised iRODS server
        """

    def __init__(self):
        """
        Constructor.
        """
        self.running_containers = []

    def tear_down(self):
        """
        Stops all started servers.
        """
        while len(self.running_containers) > 0:
            self.stop_server(self.running_containers.pop(0))

    def stop_server(self, container: ContainerisedIrodsServer):
        """
        Stops the given containerised iRODS server.
        :param container: the containerised iRODS server to stop
        """
        try:
            if container is not None:
                IrodsServerController._DOCKER_CLIENT.kill(container.native_object)
        except Exception:
            # TODO: Should not use such a general exception
            pass
        if container in self.running_containers:
            self.running_containers.remove(container)

    def create_connection_settings_volume(self, config_file_name: str, irods_server: IrodsServer) -> str:
        """
        Creates a directory with iRODS config settings that can be used to supply the iRODS settings if mounted as a
        volume at `~/.irods`.
        :param config_file_name: the name of the configuration file to write
        :param irods_server: the iRODS server that is being connected to
        """
        temp_directory = tempfile.mkdtemp(prefix="irods-config-")
        logging.info("Created temp directory for iRODS config: %s" % temp_directory)

        connection_file = os.path.join(temp_directory, config_file_name)
        self.write_connection_settings(connection_file, irods_server)

        return temp_directory

    def _start_server(self, image_name: str, irods_version: Version, users: Sequence[IrodsUser],
                      mapped_port: int=None) -> ContainerisedIrodsServer:
        """
        Starts a containerised iRODS server and blocks until it is ready to be used.
        :param image_name: the name of the iRODS server to start
        :param irods_version: the version of iRODS that is being started
        :param users: the users that have access to the started iRODS service
        :param mapped_port: port to map iRODS to Docker host machine
        :return: the started containerised iRODS server
        """
        logging.info("Starting iRODS server in Docker container")
        container = None
        started = False

        while not started:
            container = IrodsServerController._create_container(image_name, irods_version, users, mapped_port)
            atexit.register(self.stop_server, container)
            IrodsServerController._DOCKER_CLIENT.start(container.native_object)

            started = self._wait_for_start(container)
            if not started:
                logging.warning("iRODS server did not start correctly - restarting...")
                try:
                    IrodsServerController._DOCKER_CLIENT.kill(container.native_object)
                except APIError as e:
                    if " is not running" not in self.explanation:
                        raise
        assert container is not None

        self.running_containers.append(container)
        atexit.unregister(self.stop_server)

        return container


class IrodsServerControllerClassBuilder:
    """
    Builder of iRODS server controller classes that extend `IrodsServerController` subclasses that have implemented
    `write_connection_settings` and `_wait_for_start` with only `start_server` left to implement.
    """
    def __init__(self, image_name: str, version: Version, users: Sequence[IrodsUser], superclass: type):
        """
        Constructor.
        :param image_name: the name of the docker image in which the iRODS server is ran
        :param version: the version of the iRODS server
        :param users: the users that can access the iRODS server
        :param superclass: subclass of `IrodsServerController` that implements `write_connection_settings` and
        `_wait_for_start`
        """
        self.image_name = image_name
        self.version = version
        self.users = users
        self.superclass = superclass

    def build(self) -> type:
        """
        Builds the new iRODS controller class.
        :return: the built class
        """
        def start_server(controller: IrodsServerController, mapped_port: int=None) -> ContainerisedIrodsServer:
            return controller._start_server(self.image_name, self.version, self.users, mapped_port)

        return type(
            "Irods%sServerController" % str(self.version).replace(".", "_"),
            (self.superclass, ),
            {
                "VERSION": self.version,
                "IMAGE_NAME": self.image_name,
                "USERS": self.users,
                "start_server": start_server
            }
        )


class StaticIrodsServerController(metaclass=ABCMeta):
    """
    Static iRODS server controller.
    """
    @staticmethod
    @abstractmethod
    def start_server(mapped_port: int=None) -> ContainerisedIrodsServer:
        """
        Starts a containerised iRODS server and blocks until it is ready to be used.
        :param mapped_port: map iRODS's connection port to this port on the machine running docker
        :return: the started containerised iRODS server
        """

    @staticmethod
    @abstractmethod
    def stop_server(container: ContainerisedIrodsServer):
        """
        Stops the given containerised iRODS server.
        :param container: the containerised iRODS server to stop
        """

    @staticmethod
    @abstractmethod
    def tear_down():
        """
        Stops all started servers
        """

    @staticmethod
    @abstractmethod
    def write_connection_settings(file_location: str, irods_server: IrodsServer):
        """
        Writes the connection settings for the given iRODS server to the given location.
        :param file_location: the location to write the settings to (file should not already exist)
        :param irods_server: the iRODS server to create the connection settings for
        """


def create_static_irods_server_controller(irods_server_controller: IrodsServerController) \
        -> Type[StaticIrodsServerController]:
    """
    Creates a static iRODS server controller from the given iRODS server controller. This essentially makes the given
    controller a singleton in a (static) sheep's clothing.
    :param irods_server_controller:
    :return:
    """
    static_controller = type(
        "%sFactory" % type(irods_server_controller).__name__.replace("Controller", ""),
        (StaticIrodsServerController,),
        dict()
    )
    static_controller.start_server = irods_server_controller.start_server
    static_controller.stop_server = irods_server_controller.stop_server
    static_controller.write_connection_settings = irods_server_controller.write_connection_settings
    static_controller.tear_down = irods_server_controller.tear_down
    return static_controller
