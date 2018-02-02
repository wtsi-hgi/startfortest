import logging
import os
from typing import List, Any, Set

from docker.errors import ImageNotFound

from useintest.common import docker_client

CLI_ARGUMENTS = "\"$@\""

SHEBANG = "#!/usr/bin/env bash"
FAIL_SETTINGS = "set -eu -o pipefail"


def write_commands(location: str, commands: str):
    """
    Writes the commands to a file at the given location. Will overwrite any pre-existing file.
    :param location: the location to write the commands to
    :param commands: the commands to write
    """
    with open(location, "w") as file:
        file.write("%s\n" % SHEBANG)
        file.write("%s\n" % FAIL_SETTINGS)
        file.write(commands)
    os.chmod(location, 0o700)


def pull_docker_image(image: str, tag: str=None):
    """
    TODO
    :param image:
    :param tag:
    :return:
    """
    # Ensure the image with the real binaries have been pulled to stop it polluting the output
    if ":" in image:
        if tag is not None:
            raise ValueError("Cannot specify tag when tag has been passed in the image parameter")
        repository, tag = image.split(":")
    else:
        repository, tag = image, tag

    try:
        docker_client.images.get(f"{repository}:{tag}")
    except ImageNotFound:
        pull_stream = docker_client.api.pull(repository, tag=tag, stream=True)
        for line in pull_stream:
            # TODO: Remove logging to root logger
            logging.debug(line)


# TODO: Test this
def get_all_path_like_arguments_for_mounting(arguments: List[Any], allow_relative_paths: bool=True) -> Set[str]:
    """
    TODO
    :param arguments:
    :param allow_relative_paths:
    :return:
    """
    mounts = set()  # type: Set[str]
    for argument in arguments:
        if allow_relative_paths:
            argument = os.path.abspath(argument)
        if argument.startswith(os.path.sep):
            mounts.add(os.path.dirname(argument))
    return mounts
