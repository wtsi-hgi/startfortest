import base64
import os
import sys
from typing import Set

from dill import dill

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../"))

if __name__ == "__main__":
    if len(sys.argv) <= 2:
        print("")
        exit(0)

    serialised_parser = sys.argv[1]
    arguments = sys.argv[2:]

    parser = dill.loads(base64.b64decode(serialised_parser))
    mounts = parser(arguments)

    absolute_paths = False
    processed_mounts = set()    # type: Set[str]
    for path in mounts:
        if not os.path.isabs(path):
            absolute_paths = True
        if not os.path.exists(path) or os.path.isfile(path):
            path = os.path.dirname(path)
        path = os.path.abspath(path)
        if os.path.exists(path):
            # Helping wildcard mounts to work by checking for existence before adding to the mount set
            processed_mounts.add(path)

    if absolute_paths:
        # TODO: The correct thing to do here is modify all the arguments so they use absolute paths instead of relative
        # ones. However, this is too much of a parsing nightmare for me to be motivated to do it at the moment. This
        # alternative solution will break Docker images where the entrypoint uses relative paths (as the work directory
        # would have been changed).
        print("-w %s " % os.path.abspath(""), end="")

    print(" ".join(["-v {mount}:{mount}".format(mount=mount) for mount in processed_mounts]), end="")
