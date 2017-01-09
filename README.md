[![Build Status](https://travis-ci.org/wtsi-hgi/useintest.svg)](https://travis-ci.org/wtsi-hgi/useintest)
[![codecov.io](https://codecov.io/gh/wtsi-hgi/useintest/graph/badge.svg)](https://codecov.io/github/wtsi-hgi/useintest)
# Use In Test
*I don't care how it's done, I just want to use it in my tests!*

## Introduction
### Key Features
- Simple way of running services (e.g. Mongo, CouchDB, iRODS) and using executables (e.g. Samtools, icommands).
- No knowledge of containers required.
- No knowledge of service/executables required (how to install it, when it's ready to use, etc.).
- Does not require the installation of anything on your local machine, aside from Docker.
- Makes it simple to test against multiple versions of the same service or set of executables.
- Easy to achieve test isolation.

### Why use this library?
Software no longer works in isolation; with the trend towards microservices over monoliths, modern day applications 
rely on numerous external services for both data and computation.

Mocks can be a quick way to test against something that (should) behave like the external service that your 
application uses. However, unless a well respected mocking framework exists, the mock you'll end up with will probably 
make the same bad assumptions about the behaviour of service as your faulty code does!

Testing with the "real thing" or a shared dev mirror of it is probably not a good idea during development, 
particularly if the services that you're using hold state. You want to be able to run the tests in parallel, have 
repeatability and have availability, be it for when you're offline or for collaborators outside of your organisation. 
You also want to be able to wipe the slate clean and start again if something goes terribly wrong! It is unlikely you'll
be able to do this in any kind of shared environment.

This library offers a way to just start up services and then throw them away after each test case, with no mess left 
over on your machine. It gives complete test isolation along with confidence that you're testing with services similar 
to those used in production.


## How to use?
### Prerequisites
- Python >= 3.6
- Docker >= 1.12.5 (must be running)

### Installation
Bleeding edge versions can be installed directly from GitHub:
```bash
$pip install https://github.com/wtsi-hgi/useintest@master#useintest
```

### Use
#### Overview
This example shows how this library enables services to be used in tests:
```python
from useintest.predefined.mongo import MongoServiceController

# Starts a containerised version of Mongo
controller = MongoServiceController()              
service = controller.start_service()      
run_my_tests(my_application, service.host, service.port)
controller.stop_service(service)
```

This example shows how this library enables executables to be used in tests:
```python
from useintest.predefined.samtools import SamtoolsExecutablesController

controller = SamtoolsExecutablesController()  
executables_directory = controller.write_executables()
# In the case of Samtools, there will be one executable in `executables_directory` named "samtools"
run_my_tests(my_application, executables_directory)
controller.tear_down()
```



#### Predefined Services and Executables
##### Mongo
In the `useintest.predefined.mongo` module:
- `MongoServiceController`: Latest version of Mongo available.
- `Mongo3ServiceController`: Mongo version 3.

##### CouchDB:
In the `useintest.predefined.couchdb` module:
- `CouchDBServiceController`: Latest version of CouchDB available.
- `CouchDB1_6Controller`: CouchDB version 1.6.

##### iRODS
###### Services (iCAT, i.e. the iRODS server)
In the `useintest.predefined.irods.services` module:
- `IrodsServiceController`: Latest version of iRODS available.  
- `Irods4_1_10ServiceController`: iRODS version 4.1.10.
- `Irods4_1_9ServiceController`: iRODS version 4.1.9.
- `Irods4_1_8ServiceController`: iRODS version 4.1.8.
- `Irods3_3_1ServiceController`: iRODS version 3.3.1.

###### Executables (i.e. the icommands)
In the `useintest.predefined.irods.executables` module:
- `IrodsServiceController`: Latest version of iRODS available.  
- `Irods4_1_10ExecutablesController`: iRODS version 4.1.10.
- `Irods4_1_9ExecutablesController`: iRODS version 4.1.9.
- `Irods4_1_8ExecutablesController`: iRODS version 4.1.8.
- `Irods3_3_1ExecutablesController`: iRODS version 3.3.1.

_Note: Use `authenticate` (or `write_executables_and_authenticate`) to handle authentication to the iRODS before use._

###### Helpers
In the `useintest.predefined.irods.helpers` module:
- `IrodsSetupHelper`: class to help with setup of tests with iRODS (works with any supported version of iRODS).

##### Samtools
In the `useintest.predefined.samtools` module:
- `SamtoolsExecutablesController`: Latest version of samtools available.
- `Samtools1_3_1ExecutablesController`: Samtools version 1.3.1 (using htslib 1.3.1).
