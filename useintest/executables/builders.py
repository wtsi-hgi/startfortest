import argparse
import base64
import os
import sys
from copy import deepcopy
from typing import List, Iterable, Dict, Set, Callable, Any, Union

from dill import dill

from useintest.executables.common import CLI_ARGUMENTS

_PROJECT_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")
_ARGUMENTS_TO_MOUNT_SCRIPT = os.path.join(_PROJECT_DIRECTORY, "executables", "paths_to_mount.py")


class CommandsBuilder:
    """
    Builds commands to run an executable in Docker.
    """
    def __init__(self, executable: str=None, container: str=None, image: str=None, executable_arguments: List[str]=None,
                 get_path_arguments_to_mount: Callable[[List[Any]], Set[str]]=None,
                 ports: Dict[int, int]=None, mounts: Dict[str, Union[str, Set[str]]]=None,
                 variables: Iterable[str]=None, name: str=None, detached: bool=False, other_docker: str=""):
        self.executable = executable
        self.container = container
        self.image = image
        self.executable_arguments = executable_arguments
        self.get_path_arguments_to_mount = get_path_arguments_to_mount \
            if get_path_arguments_to_mount is not None else lambda arguments: set()
        self.ports = ports if ports is not None else dict()
        self.mounts = mounts if mounts is not None else dict()
        self.variables = variables if variables is not None else {}
        self.name = name
        self.detached = detached
        self.other_docker = other_docker

    def build(self) -> str:
        """
        Builds the commands.
        :return: build comamnds.
        """
        if self.container is None and self.image is None:
            raise ValueError("Must define either the Docker image or container to run commands in")
        if self.container is not None and self.image is not None:
            raise ValueError("Cannot build Docker command to work in for both an image and a running container")

        mounts = ""
        for local_volume, container_volumes in self.mounts.items():
            if not isinstance(container_volumes, set):
                container_volumes = {container_volumes}
            for container_volume in container_volumes:
                mounts += "-v %s:%s " % (local_volume, container_volume)

        ports = ""
        for local_port, container_port in self.ports.items():
            ports += "-p %d:%d" % (local_port, container_port)

        variables = ""
        for variable in self.variables:
            variables += "-e %s " % variable

        executable_arguments = " ".join(self.executable_arguments) if self.executable_arguments is not None else CLI_ARGUMENTS

        if self.get_path_arguments_to_mount is not None:
            serialised_arguments_parser = base64.b64encode(dill.dumps(self.get_path_arguments_to_mount)).decode("utf-8")

            calculate_additional_mounts = ("""
                $("%(python_interpreter)s" "%(python_arguments_script)s" "%(serialised_arguments_parser)s" %(cli_arguments)s)
            """ % {
                "python_interpreter": sys.executable,
                "python_arguments_script": _ARGUMENTS_TO_MOUNT_SCRIPT,
                "serialised_arguments_parser": serialised_arguments_parser,
                "cli_arguments": executable_arguments
            }).strip()
        else:
            calculate_additional_mounts = ""

        return """
            docker %(docker_noun)s -i \\
                %(name)s \\
                %(detached)s \\
                %(mounts)s %(calculate_additional_mounts)s \\
                %(ports)s \\
                %(variables)s \\
                %(other_docker)s \\
                %(image_or_container)s \\
                %(executable)s %(executable_arguments)s
        """ % {
            "calculate_additional_mounts": calculate_additional_mounts,
            "name": "--name %s" % self.name if self.name is not None else "",
            "detached": "-d" if self.detached else "",
            "mounts": mounts,
            "ports": ports,
            "variables": variables,
            "other_docker": self.other_docker,
            "docker_noun": "run" if self.image is not None else "exec",
            "image_or_container": self.image if self.image is not None else self.container,
            "executable": self.executable,
            "executable_arguments": executable_arguments
        }


class MountedArgumentParserBuilder:
    """
    TODO
    """
    ALL_POSITIONAL_ARGUMENTS = "*"

    def __init__(self, named_arguments: Set[str]=None, positional_arguments: Union[Set[int], str]=None):
        """
        TODO
        :param named_arguments:
        :param positional_arguments:
        """
        self.named_arguments = named_arguments if named_arguments is not None else set()
        self.positional_arguments = positional_arguments if positional_arguments is not None else set()

    def build(self) -> Callable[[List[Any]], Set[str]]:
        """
        TODO
        :return:
        """
        named_arguments = deepcopy(self.named_arguments)
        positional_arguments = deepcopy(self.positional_arguments)

        def get_mounts(cli_arguments: List[Any]) -> Set[str]:
            parser = argparse.ArgumentParser()
            for name in named_arguments:
                parser.add_argument(name, type=str)
            parser.add_argument("positional_arguments", type=str, nargs="*")
            arguments, _ = parser.parse_known_args(cli_arguments)

            mounts = set()  # type: Set[str]

            for name in named_arguments:
                value = getattr(arguments, name.lstrip("-"), None)
                if value is not None:
                    mounts.add(value)

            if positional_arguments != MountedArgumentParserBuilder.ALL_POSITIONAL_ARGUMENTS:
                for position in positional_arguments:
                    if position <= len(arguments.positional_arguments):
                        mounts.add(arguments.positional_arguments[position - 1])
            else:
                mounts = mounts.union(set(arguments.positional_arguments))

            return mounts

        return get_mounts
