from useintest.executables.builders import CommandsBuilder
from useintest.executables.common import get_all_path_like_arguments_for_mounting
from useintest.executables.controllers import DefinedExecutablesControllerTypeBuilder
from useintest.executables.models import Executable

Samtools1_3_1ExecutablesController = DefinedExecutablesControllerTypeBuilder(
    "Samtools1_3_1ExecutablesController",
    {
        "samtools": Executable(
            CommandsBuilder(
                image="comics/samtools:1.3.1",
                executable="samtools",
                # There are so many ways in which Samtools accepts file paths that the creation of a parser for it would
                # be a massive task. Instead, we'll overzealously bind mount anything that looks like a file path.
                get_path_arguments_to_mount=get_all_path_like_arguments_for_mounting
            ),
            False
        )
    }
).build()

SamtoolsExecutablesController = Samtools1_3_1ExecutablesController

samtools_executable_controllers = {Samtools1_3_1ExecutablesController}
