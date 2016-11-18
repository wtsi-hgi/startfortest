import atexit
import logging
import math
from abc import ABCMeta, abstractmethod
from threading import Lock, Thread, Event
from typing import Dict, Iterator, Optional, List

from docker.errors import APIError

from bringupfortest.exceptions import ContainerStartException
from bringupfortest.models import Container
from hgicommon.docker.client import create_client
from hgicommon.helpers import create_random_string, get_open_port

_logger = logging.getLogger(__name__)


class Controller(metaclass=ABCMeta):
    """
    TODO
    """
    @abstractmethod
    def read_next_log_line(self, container: Container) -> str:
        """
        TODO
        :param container:
        :return:
        """

    @abstractmethod
    def _start(self) -> Container:
        """
        TODO
        """

    @abstractmethod
    def _stop(self):
        """
        TODO
        """

    def __init__(self, start_timeout: int=math.inf, start_retries: int=math.inf, stop_on_exit: bool=True):
        self.start_timeout = start_timeout
        self.start_retries = start_retries
        self.stop_on_exit = stop_on_exit

    def start(self) -> Container:
        """
        TODO
        :return:
        """
        container = None
        tries = 0
        started = Event()
        while not started.is_set():
            if tries > self.start_retries:
                raise ContainerStartException()
            container = self._start()
            # FIXME: Thread needs to stop safely!
            Thread(target=self._wait_until_started).start()
            started.wait(timeout=self.start_timeout)
            tries += 1
        assert container is not None
        return container

    def stop(self, container: Container):
        """
        TODO
        :return:
        """

    def _wait_until_started(self, container: Container, wait_lock: Lock):
        """
        TODO
        :param container:
        """
        while not self._stop_wait_check:
            line = self.read_next_log_line(container)
            logging.debug(line)
            if self.specification.started_detection(line):
                break
        wait_lock.release()


class DockerController(Controller, metaclass=ABCMeta):
    """
    TODO
    """
    _docker_client = create_client()

    @staticmethod
    def _get_docker_image(repository: str, tag: str) -> Optional[str]:
        """
        TODO
        :return: image identifier or `None` if it hasn't been pulled
        """
        identifiers = DockerController._docker_client.images("%s:%s" % (repository, tag), quiet=True)
        return identifiers[0] if len(identifiers) > 0 else None

    def __init__(self, repository: str, tag: str, exposed_ports: List[int], start_timeout: int=math.inf,
                 start_retries: int=math.inf):
        super().__init__(start_timeout, start_retries)
        self.repository = repository
        self.tag = tag
        self.exposed_ports = exposed_ports
        # TODO: Memory leak here as iterators aren't removed
        self._log_iterator = dict()     # type: Dict[Container, Iterator]

    def read_next_log_line(self, container: Container) -> str:
        if container not in self._log_iterator:
            self._log_iterator[container] = iter(
                DockerController._docker_client.logs(container.native_object, stream=True))
        return str(next(self._log_iterator[container]))

    def _start(self):
        _docker_client = DockerController._docker_client

        if self._get_docker_image(self.docker_repository, self.docker_tag) is None:
            # Docker image doesn't exist locally: getting from DockerHub
            _docker_client.pull(self.docker_repository, self.docker_tag)

        container = Container()
        container.name = create_random_string(prefix="%s-" % self.specification.docker_repository)
        container.internal_ports_map_to = {(port, get_open_port()) for port in self.specification.exposed_ports}
        container.native_object = _docker_client.create_container(
            image=self._get_docker_image(self.specification.docker_repository, self.specification.docker_tag),
            name=container.name, ports=container.internal_ports_map_to.values(),
            host_config=_docker_client.create_host_config(port_bindings=container.internal_ports_map_to))

        if self.stop_on_exit:
            atexit.register(self._stop, container)
        _docker_client.start(container.native_object)

        return container

    def _stop(self):
        try:
            DockerController._docker_client.kill(self.container.native_object)
        except Exception as e:
            ignore = False
            if isinstance(e, APIError):
                ignore = "is not running" in str(e.explanation)
            if not ignore:
                raise e
