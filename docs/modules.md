# Modules
_Predefined services and executables_


## Mongo
### Module
`useintest.modules.mongo`

### Contents
* `MongoServiceController`: Latest supported version of Mongo available.
* `Mongo3ServiceController`: Mongo version 3.

### Examples
To use a containerised version of Mongo in a test:
```python
from useintest.modules.mongo import MongoServiceController

controller = MongoServiceController()              
with controller.start_service() as service:      
    run_my_test(my_application, service.host, service.port)
```


## CouchDB
### Module
`useintest.predefined.couchdb`

### Contents
* `CouchDBServiceController`: Latest supported version of CouchDB available.
* `CouchDB1_6Controller`: CouchDB version 1.6.

### Examples
To use a containerised version of Couchdb in a test:
```python
from useintest.predefined.couchdb import CouchDBServiceController

controller = CouchDBServiceController()              
with controller.start_service() as service:      
    run_my_test(my_application, service.host, service.port)
```


## iRODS
### Module
`useintest.predefined.irods`

### Contents
#### Services (i.e. the iRODS server)
* `IrodsServiceController`: Latest supported version of iRODS available.
* `Irods4_1_10ServiceController`: iRODS version 4.1.10.

#### Executables (i.e. the icommands)
* `IrodsExecutablesController`: Latest supported version of iRODS available.
* `Irods4_1_10ExecutablesController`: iRODS version 4.1.10.

#### Helpers
- `IrodsSetupHelper`: class to help with setup of tests with iRODS (works with any supported version of iRODS).

### Examples
The easiest way to use iRODS in your test is to use the `setup` method, which start the iRODS server, creates the 
icommands on the host machine and then deals with authentication. The end result is a set of icommands that are ready to 
use against a clean iRODS server:
```python
from useintest.predefined.irods import setup_irods

# Optionally define the service controller (i.e. the version of iRODS) with the `irods_service_controller` parameter
icommands_location, service, icommands_controller, icat_controller = setup_irods()
run_my_test(my_application, icommands_location)

# Tear down (should be in try-finally)
icat_controller.stop_service(service)
icommands_controller.tear_down()
```

Alternatively, to just set up an iRODS service ("iCAT"):
```python
from useintest.predefined.irods import IrodsServiceController

# Setup iRODS server
controller = IrodsServiceController()
with controller.start_service() as service:
    run_my_test(my_application, service.host, service.port)
```

To setup corresponding icommands for an iRODS service:
```python
import os
import shutil
from useintest.predefined.irods import IrodsServiceController, IrodsExecutablesController

# Write iRODS connection settings for the server
settings_directory = "/tmp/irods"
os.makedirs(settings_directory)
config_file = os.path.join(settings_directory, icat_controller.config_file_name)
password = IrodsServiceController.write_connection_settings(config_file, service)

# Setup iRODS executables
irods_executables_controller = IrodsExecutablesController(service.name, settings_directory)
icommands_location = irods_executables_controller.write_executables_and_authenticate(password)

# Use the iRODS server in test
run_my_test(my_application, service.host, service.port)

# Cleanup (should be in a try-catch!)
irods_executables_controller.tear_down()
shutil.rmtree(settings_directory)
```

For help in setting up tests there is `IrodsSetupHelper`:
```python
from useintest.predefined.irods import IrodsSetupHelper

setup_irods
setup_helper = IrodsSetupHelper(icommands_location)
```


## Samtools
### Module
`useintest.predefined.samtools`

### Contents
* `SamtoolsExecutablesController`: Latest supported version of samtools available.
* `Samtools1_3_1ExecutablesController`: Samtools version 1.3.1 (using htslib 1.3.1).

### Examples
To use containerised Samtools executable in a test:
```python
from useintest.predefined.samtools import SamtoolsExecutablesController

controller = SamtoolsExecutablesController()
executables_directory = controller.write_executables()
run_my_test(my_application, executables_directory)
controller.tear_down()
```

### Warnings
Directories containing files that are arguments to Samtools are bind-mounted to the Docker container. Therefore, be 
aware that if you call:
```bash
$ ${executables_directory}/samtools /tmp
```
the controller will try to bind-mount the root directory of your local machine to the root directory of the Docker 
container - the result would not be pretty.


## GitLab
### Module
`useintest.predefined.gitlab`

### Contents
* `GitLabServiceController`: Latest supported version of GitLab available.
* `GitLab8_16_6_ce_0ServiceController`: GitLab 8.16.6-ce.0.
* `GitLab8_13_11_ce_0ServiceController`: GitLab 8.13.11-ce.0.
* `GitLab8_10_4_ce_0ServiceController`: GitLab 8.10.4-ce.0.

### Examples
To use containerised GitLab in a test:
```python
from useintest.predefined.gitlab import GitLabServiceController

controller = GitLabServiceController()
with controller.start_service() as service:
    run_my_test(my_application, service.host, service.ports[80], service.root_user.username, service.root_user.password)
```

#### Helpers
- `SshKey`: class to generate temporary files containing private/public SSH keys, which can be used with GitLab.
```python
from useintest.modules.gitlab import SshKey

with SshKey() as ssh_key:
    add_ssh_key(user, public_key_file=ssh_key.public_key_file)
    push_things(gitlab_url, private_key_file=ssh_key.private_key_file)
# The temp files containg the public and private keys have been removed 
```
   

## Gogs
### Module
`useintest.modules.gogs`

### Contents
* `GogsServiceController`: Latest supported version of Gogs.
* `Gogs0_11_4ServiceController`: Gogs 0.11.4.

### Examples
To use containerised Gogs in a test:
```python
from useintest.modules.gogs import GogsServiceController

controller = GogsServiceController()
with controller.start_service() as service:
    run_my_test(my_application, service.host, service.port, service.root_user.username, service.root_user.password)
```


## Bissell
_[Dummy iRobot server for client testing](https://github.com/wtsi-hgi/bissell)._

### Module
`useintest.modules.bissel`

### Contents
* `BissellServiceController`: Latest supported version of Bissell.

### Examples
To use containerised Bissell in a test:
```python
from useintest.modules.bissell import BissellServiceController
import requests

controller = BissellServiceController()
with controller.start_service() as service:
    response = requests.head(f"http://{service.host}:{service.port}")
```


## Consul
### Module
`useintest.modules.consul`

### Contents
* `ConsulServiceController`: Latest supported version of Consul available.
* `Consul1_0_0ServiceController`: Consul 1.0.0.
* `Consul0_8_4_ServiceController`: Consul 0.8.4.

### Examples
To use containerised Consul in a test:
```python
from useintest.modules.consul import ConsulServiceController
# Dependency on `python-consul` (https://github.com/cablehead/python-consul) is only required if using 
# `service.create_consul_client`
from consul import Consul

controller = ConsulServiceController()
with controller.start_service() as service:
    run_my_test(my_application, service.create_consul_client())
```

To set the value of environment variables associated to a Consul service, such as `CONSUL_HTTP_ADDR`, use:
```python
service.setup_environment()
```
