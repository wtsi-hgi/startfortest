import atexit
import logging
import os
import shutil
from enum import Enum, unique
from typing import Union

from testwithbaton._common import create_client
from testwithbaton._irods_server import create_irods_test_server, start_irods
from testwithbaton.models import IrodsServer, IrodsUser, BatonDockerBuild
from testwithbaton._proxies import build_baton_docker, create_baton_proxy_binaries, create_icommands_proxy_binaries

_DEFAULT_BATON_DOCKER_BUILD = BatonDockerBuild(
    "github.com/wtsi-hgi/docker-baton.git",
    "wtsi-hgi/baton:0.16.1",
    "0.16.1/irods-3.3.1/Dockerfile"
)


class IrodsEnvironmentKey(Enum):
    """
    Keys of environment variables that may be used to define an iRODS server that can be loaded using
    `get_irods_server_from_environment_if_defined`.
    """
    IRODS_HOST = "IRODS_HOST"
    IRODS_PORT = "IRODS_PORT"
    IRODS_USERNAME = "IRODS_USERNAME"
    IRODS_PASSWORD = "IRODS_PASSWORD"
    IRODS_ZONE = "IRODS_ZONE"


def get_irods_server_from_environment_if_defined() -> Union[None, IrodsServer]:
    """
    Instantiates an iRODS server that has been defined through environment variables. If no definition/an incomplete
    definition was found, returns `None`.
    :return: a representation of the iRODS server defined through environment variables else `None` if no definition
    """
    for key in IrodsEnvironmentKey:
        environment_value = os.environ.get(key.value)
        if environment_value is None:
            return None

    return IrodsServer(
        os.environ[IrodsEnvironmentKey.IRODS_HOST.value],
        int(os.environ[IrodsEnvironmentKey.IRODS_PORT.value]),
        [IrodsUser(
            os.environ[IrodsEnvironmentKey.IRODS_USERNAME.value],
            os.environ[IrodsEnvironmentKey.IRODS_PASSWORD.value],
            os.environ[IrodsEnvironmentKey.IRODS_ZONE.value],
        )]
    )


class TestWithBatonSetup:
    """
    A setup for testing with baton.
    """
    @unique
    class _SetupState(Enum):
        """
        States of a `TestWithBatonSetup` instance.
        """
        INIT = 0,
        RUNNING = 1,
        STOPPED = 2

    def __init__(
            self, irods_test_server: IrodsServer=None, baton_docker_build: BatonDockerBuild=_DEFAULT_BATON_DOCKER_BUILD):
        """
        Constructor.
        :param irods_test_server: a pre-configured, running iRODS server to use in the tests
        :param baton_docker_build: baton Docker that is to be built and used
        """
        # Ensure that no matter what happens, tear down is done
        atexit.register(self.tear_down)

        self.irods_test_server = irods_test_server
        self._external_irods_test_server = irods_test_server is not None
        self._state = TestWithBatonSetup._SetupState.INIT
        self._baton_docker_build = baton_docker_build

        self.baton_location = None
        self.icommands_location = None

    def setup(self):
        """
        Sets up the setup: builds the baton Docker image, starts the iRODS test server (if required) and creates the
        proxies.
        """
        if self._state != TestWithBatonSetup._SetupState.INIT:
            raise RuntimeError("Already been setup")
        self._state = TestWithBatonSetup._SetupState.RUNNING

        # Build baton Docker
        docker_client = create_client()
        logging.debug("Building baton Docker")
        build_baton_docker(docker_client, self._baton_docker_build)

        if not self._external_irods_test_server:
            logging.debug("Creating iRODS test server")
            self.irods_test_server = create_irods_test_server(docker_client)
            logging.debug("Starting iRODS test server")
            start_irods(docker_client, self.irods_test_server)
        else:
            logging.debug("Using pre-existing iRODS server")

        logging.debug("Creating proxies")
        self.baton_location = create_baton_proxy_binaries(
                self.irods_test_server, self._baton_docker_build.build_name)
        self.icommands_location = create_icommands_proxy_binaries(
                self.irods_test_server, self._baton_docker_build.build_name)
        logging.debug("Setup complete")

    def tear_down(self):
        """
        Tear down the test environment.
        """
        if self._state == TestWithBatonSetup._SetupState.RUNNING:
            self._state = TestWithBatonSetup._SetupState.STOPPED
            atexit.unregister(self.tear_down)

            if not self._external_irods_test_server:
                self._tear_down_irods_test_server()
            else:
                logging.debug("External iRODS test server used - not tearing down")

            logging.debug("Removing temp folders")
            TestWithBatonSetup._tear_down_temp_directory(self.baton_location)
            TestWithBatonSetup._tear_down_temp_directory(self.icommands_location)
            self.baton_location = None
            self.icommands_location = None

            logging.debug("Tear down complete")

    def _tear_down_irods_test_server(self):
        """
        Tears down the iRODS test server.
        """
        assert not self._external_irods_test_server
        logging.debug("Killing iRODS test server")
        docker_client = create_client()
        try:
            docker_client.kill(self.irods_test_server.container)
        except Exception as error:
            logging.error(error)
        self.irods_test_server = None

    @staticmethod
    def _tear_down_temp_directory(directory: str):
        """
        Safely tears down the given temporary directory.
        :param directory: the directory to tear down
        """
        try:
            shutil.rmtree(directory)
        except Exception as error:
            logging.error(error)
