import os

import logging
from typing import List, Any, Set

from hgicommon.docker.client import create_client

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


def pull_docker_image(image: str):
    """
    TODO
    :param image:
    :return:
    """
    # Ensure the image with the real binaries have been pulled to stop it polluting the output
    if ":" in image:
        repository, tag = image.split(":")
    else:
        repository, tag = image, None
    docker_client = create_client()
    docker_image = docker_client.images("%s:%s" % (repository, tag), quiet=True)
    if len(docker_image) == 0:
        for line in docker_client.pull(image, stream=True):
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
