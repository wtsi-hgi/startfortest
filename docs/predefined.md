# Predefined Services and Executables
## Mongo
### Module
`useintest.predefined.mongo`

### Contents
* `MongoServiceController`: Latest version of Mongo available.
* `Mongo3ServiceController`: Mongo version 3.

### Examples
To use a containerised version of Mongo in a test:
```python
from useintest.predefined.mongo import MongoServiceController

controller = MongoServiceController()              
service = controller.start_service()      
run_my_test(my_application, service.host, service.port)
controller.stop_service(service)
```


## CouchDB
### Module
`useintest.predefined.couchdb`

### Contents
* `CouchDBServiceController`: Latest version of CouchDB available.
* `CouchDB1_6Controller`: CouchDB version 1.6.

### Examples
To use a containerised version of Couchdb in a test:
```python
from useintest.predefined.couchdb import CouchDBServiceController

controller = CouchDBServiceController()              
service = controller.start_service()      
run_my_test(my_application, service.host, service.port)
controller.stop_service(service)
```


## iRODS
### Module
`useintest.predefined.irods`

### Contents
#### Services (i.e. the iRODS server)
* `IrodsServiceController`: Latest version of iRODS available.  
* `Irods4_1_10ServiceController`: iRODS version 4.1.10.
* `Irods4_1_9ServiceController`: iRODS version 4.1.9.
* `Irods4_1_8ServiceController`: iRODS version 4.1.8.
* `Irods3_3_1ServiceController`: iRODS version 3.3.1.

#### Executables (i.e. the icommands)
* `IrodsExecutablesController`: Latest version of iRODS available.  
* `Irods4_1_10ExecutablesController`: iRODS version 4.1.10.
* `Irods4_1_9ExecutablesController`: iRODS version 4.1.9.
* `Irods4_1_8ExecutablesController`: iRODS version 4.1.8.
* `Irods3_3_1ExecutablesController`: iRODS version 3.3.1.

#### Helpers
- `IrodsSetupHelper`: class to help with setup of tests with iRODS (works with any supported version of iRODS).

### Examples
```python
import os
import shutil
from useintest.predefined.irods import IrodsServiceController, IrodsExecutablesController, IrodsSetupHelper

# Setup iRODS server
icat_controller = IrodsServiceController()
service = icat_controller.start_service()

# Write iRODS connection settings for the server
settings_directory = "/tmp/irods"
os.makedirs(settings_directory)
config_file = os.path.join(settings_directory, icat_controller.config_file_name)
password = IrodsServiceController.write_connection_settings(config_file, service)

# Setup iRODS executables
irods_executables_controller = IrodsExecutablesController(service.name, settings_directory)
icommands_location = irods_executables_controller.write_executables_and_authenticate(password)

# This can be used to help setup tests
setup_helper = IrodsSetupHelper(icommands_location)

# Cleanup (should be in a try-catch!)
irods_executables_controller.tear_down()
shutil.rmtree(settings_directory)
```


## Samtools
### Module
`useintest.predefined.samtools`

### Contents
* `SamtoolsExecutablesController`: Latest version of samtools available.
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
