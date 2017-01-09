import subprocess
from typing import List, Tuple, Optional

from useintest.tests.common import MAX_RUN_TIME_IN_SECONDS
from useintest.executables.builders import CommandsBuilder

UBUNTU_IMAGE_TO_TEST_WITH = "ubuntu:16.04"


def get_builder_for_commands_to_run_persistent_ubuntu() -> CommandsBuilder:
    """
    Gets commands builder to run a persistent Ubuntu container.
    :return: the commands builder
    """
    return CommandsBuilder("sleep", image=UBUNTU_IMAGE_TO_TEST_WITH, executable_arguments=["infinity"])


def run(arguments: List=None, raise_if_stderr: bool=True, pipe_in: str=None, decode_output_to: Optional[str]="utf-8") \
        -> Tuple[str, str]:
    """
    Calls out to run the given arguments on the system.
    :param arguments: the arguments to execute, where the first item is the executable and subsequent items are the
    executable's arguments
    :param raise_if_stderr: whether the test should raise an exception if anything is written to standard error
    :param pipe_in: any string that should be piped into the process as input
    :param decode_output_to: the output character encoding
    :return: tuple where the first element is what was written to standard out and the second is what was written to
    standard error
    """
    if pipe_in is not None and isinstance(pipe_in, str):
        pipe_in = str.encode(pipe_in)

    process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = process.communicate(input=pipe_in, timeout=MAX_RUN_TIME_IN_SECONDS)
    if decode_output_to is not None:
        out = out.decode(decode_output_to).rstrip("\n")
        error = error.decode(decode_output_to)

    if raise_if_stderr and len(error) > 0:
        raise ValueError("Unexpected output on standard error:\n%s" % error)

    return out, error
