[![Build Status](https://travis-ci.org/wtsi-hgi/test-with-irods.svg)](https://travis-ci.org/wtsi-hgi/test-with-irods)
[![codecov.io](https://codecov.io/github/wtsi-hgi/test-with-irods/coverage.svg?branch=master)](https://codecov.io/github/wtsi-hgi/test-with-irods?branch=master)

# Test with iRODS
Test with iRODS exploits [Docker](http://docker.com) to simplify the testing of software that interacts with an iRODS 
(iCAT) server.


## Use
TODO: add useful details here...


### Setup Helper
To help with the setup of tests, a number of helper methods are available:
```python
from testwithirods.helpers import SetupHelper, AccessLevel
from testwithirods.models import IrodsResource, IrodsUser, Metadata

setup_helper = SetupHelper("icommands_location")
setup_helper.create_data_object("name", contents="contents")   # type: str
setup_helper.replicate_data_object("/path/to/data_object", "resourceName")
setup_helper.create_collection("name")   # type: str
setup_helper.add_metadata_to("/path/to/entity", Metadata({"attribute": "value"}))
setup_helper.get_checksum("/path/to/entity")   # type: str
setup_helper.create_replica_storage()   # type: IrodsResource
setup_helper.create_user("username", "zone")    # type: IrodsUser
setup_helper.set_access("username_or_group", AccessLevel.OWN, "/path/to/entity")
setup_helper.run_icommand(["icommand_binary", "--any", "arguments"])    # type: str
```


## Specifying the Docker Daemon
It is possible to specify the Docker daemon that you wish to use by setting environment variables. In particular, 
`DOCKER_TLS_VERIFY`, `DOCKER_HOST` and `DOCKER_CERT_PATH` can be set. For example, the configuration's environment
variables could be:
```bash
DOCKER_TLS_VERIFY=1
DOCKER_HOST=tcp://192.168.99.100:2376
DOCKER_CERT_PATH=/Users/you/.docker/machine/machines/default
```
*[Information on how to set these variables in Pycharm.](https://www.jetbrains.com/pycharm/help/run-debug-configuration-python.html#d427982e277)*

If these variables are not set, it is assumed the daemon is accessible via the default UNIX socket: 
`unix:///var/run/docker.sock`.


## Development
### Setup
Install both the library dependencies and the dependencies needed for testing:
```bash
$ pip3 install -q -r requirements.txt
$ pip3 install -q -r test_requirements.txt
```

### Testing
Using nosetests, in the project directory, run:
```bash
$ nosetests -v
```

To generate a test coverage report with nosetests:
```bash
$ nosetests -v --with-coverage --cover-package=testwithirods --cover-inclusive
```

To limit testing to a specific version iRODS, set the environment variable `SINGLE_TEST_SETUP` to match 
the name of the controller associated to the server, e.g. 
`SINGLE_TEST_SETUP=Irods4_1_8ServerController`.