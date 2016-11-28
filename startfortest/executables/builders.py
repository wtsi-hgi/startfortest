import os
import sys
from typing import List, Iterable, Dict

from startfortest.executables.common import CLI_ARGUMENTS

_PROJECT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
_ARGUMENTS_TO_MOUNT_SCRIPT = os.path.join(_PROJECT_DIRECTORY, "executables", "paths_to_mount.py")


class CommandsBuilder:
    """
    Builds commands to run an executable in Docker.
    """
    def __init__(self, executable: str, container: str=None, image: str=None, executable_arguments: List[str]=None,
                 named_path_arguments_to_mount: Iterable[str]=None, positional_path_arguments_to_mount: List[int]=None,
                 ports: Dict[int, int]=None, mounts: Dict[str, str]=None, variables: Iterable[str]=None, name: str=None,
                 detached: bool=False, other_docker: str=""):
        self.executable = executable
        self.container = container
        self.image = image
        self.executable_arguments = executable_arguments
        self.named_path_arguments_to_mount = named_path_arguments_to_mount \
            if named_path_arguments_to_mount is not None else {}
        self.positional_path_arguments_to_mount = positional_path_arguments_to_mount \
            if positional_path_arguments_to_mount is not None else {}
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
        for local_volume, container_volume in self.mounts.items():
            mounts += "-v %s:%s" % (local_volume, container_volume)

        ports = ""
        for local_port, container_port in self.ports.items():
            ports += "-p %d:%d" % (local_port, container_port)

        variables = ""
        for variable in self.variables:
            variables += "-e %s " % variable

        executable_arguments = " ".join(self.executable_arguments) if self.executable_arguments is not None else CLI_ARGUMENTS

        if len(self.named_path_arguments_to_mount) > 0 or len(self.positional_path_arguments_to_mount) > 0:
            named_path_arguments_to_mount = " ".join(["-n %s" % name for name in self.named_path_arguments_to_mount])
            positional_path_arguments_to_mount = " ".join(["-p %s" % position for position in self.positional_path_arguments_to_mount])
            calculate_additional_mounts = ("""
                $("%(python_interpreter)s" "%(python_arguments_script)s" %(named_mounts)s %(positional_mounts)s -- %(cli_arguments)s)
            """ % {
                "python_interpreter": sys.executable,
                "python_arguments_script": _ARGUMENTS_TO_MOUNT_SCRIPT,
                "named_mounts": named_path_arguments_to_mount,
                "positional_mounts": positional_path_arguments_to_mount,
                "cli_arguments": CLI_ARGUMENTS
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
