import argparse
import logging
import os
import sys
from copy import copy
from typing import Dict, List, Set, Any, Tuple

from hgicommon.models import Model


class _Configuration(Model):
    """
    Run configuration.
    """
    def __init__(self, named_arguments_to_mount: Set[str], positional_arguments_to_mount: List[int],
                 named_arguments: Dict, positional_arguments: List):
        """
        Constructor.
        :param named_arguments_to_mount: the set of named arguments that refer to locations that are to be mounted
        :param positional_arguments_to_mount: list of positions of the positional arguments that also refer to these
        locations
        :param named_arguments: the named arguments
        :param positional_arguments: the positional arguments
        """
        self.named_arguments_to_mount = named_arguments_to_mount
        self.positional_arguments_to_mount = positional_arguments_to_mount
        self.named_arguments = named_arguments
        self.positional_arguments = positional_arguments


def _separate_arguments_by_type(arguments: List) -> Tuple[Dict, List]:
    """
    Separates arguments by type into a dictionary of named arguments and an ordered list of positional arguments.
    :param arguments: the arguments as given via the CLI
    :return: tuple where the first element is the named arguments and the second is the positional arguments
    """
    if len(arguments) == 0:
        return {}, []

    name_parameters = dict()       # type: Dict[str, Any]
    i = 0
    parameter_name = arguments[i]
    while parameter_name.startswith("-"):
        if i + 1 < len(arguments) and not arguments[i + 1].startswith("-"):
            i += 1
            value = arguments[i]
        else:
            value = None
        i += 1
        name_parameters[parameter_name.lstrip("-")] = value
        parameter_name = arguments[i]

    positional_parameters = arguments[i:]
    return name_parameters, positional_parameters


def _parse_arguments() -> _Configuration:
    """
    Parses the arguments.
    :return: the corresponding run configuration
    """
    program_arguments = copy(sys.argv[1:])

    executable_arguments = program_arguments[program_arguments.index("--") + 1:]
    program_arguments = program_arguments[0:program_arguments.index("--")]

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=str, action="append",
                        help="Named arguments that refer to locations that are to be mounted")
    parser.add_argument("-p", type=int, action="append",
                        help="Positions of positional arguments that refer to locations that are to be mounted")
    parser.add_argument("arguments", type=str, nargs="*", help="Program arguments")
    arguments = parser.parse_args(program_arguments)

    # Arguments were saved beforehand - there should be at most one string of them
    assert len(arguments.arguments) == 0

    named_arguments, positional_arguments = _separate_arguments_by_type(executable_arguments)

    return _Configuration(
        named_arguments_to_mount=set(arguments.n) if arguments.n else {},
        positional_arguments_to_mount=arguments.p if arguments.p else [],
        named_arguments=named_arguments,
        positional_arguments=positional_arguments)


def _get_paths_to_be_mounted(configuration: _Configuration) -> Set[str]:
    """
    Gets the paths to be mounted from the given configuration.
    :param configuration: the to derive the paths to be mounted from
    :return: paths to be mounted
    """
    mounts = set()  # type: Set[str]
    for parameter in configuration.named_arguments_to_mount:
        if parameter in configuration.named_arguments:
            path = configuration.named_arguments[parameter]
            mounts.add(path)

    for index in configuration.positional_arguments_to_mount:
        index -= 1
        if index < len(configuration.positional_arguments):
            path = configuration.positional_arguments[index]
            mounts.add(path)

    return mounts


if __name__ == "__main__":
    configuration = _parse_arguments()
    mounts = _get_paths_to_be_mounted(configuration)

    absolute_paths = False
    processed_mounts = set()    # type: Set[str]
    for path in mounts:
        if not os.path.isabs(path):
            absolute_paths = True
        if not os.path.exists(path) or os.path.isfile(path):
            path = os.path.dirname(path)
        path = os.path.abspath(path)
        processed_mounts.add(path)

    if absolute_paths:
        # TODO: The correct thing to do here is modify all the arguments so they use absolute paths instead of relative
        # ones. However, this is too much of a parsing nightmare for me to be motivated to do it at the moment. This
        # alternative solution will break Docker images where the entrypoint uses relative paths (as the work directory
        # would have been changed).
        print("-w %s" % os.path.abspath(""))

    print(" ".join(["-v {mount}:{mount}".format(mount=mount) for mount in processed_mounts]))
