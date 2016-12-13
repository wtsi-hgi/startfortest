from time import sleep

from startfortest.executables.builders import DefinedExecutablesControllerTypeBuilder, CommandsBuilder
from startfortest.executables.common import get_all_path_like_arguments_for_mounting
from startfortest.executables.models import Executable

Samtools1_3_1_ExecutablesController = DefinedExecutablesControllerTypeBuilder(
    "SamtoolsExecutablesController",
    {
        "samtools": Executable(
            CommandsBuilder(
                image="comics/samtools:1.3.1",
                executable="samtools",
                # There are so many ways in which Samtools accepts file paths that the creation of a parser for it would
                # be a massive task. Instead, we'll overzealously bind mount directories that look like they're used
                get_path_arguments_to_mount=get_all_path_like_arguments_for_mounting
            ),
            False
        )
    }
).build()
