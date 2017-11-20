[![Build Status](https://travis-ci.org/wtsi-hgi/useintest.svg)](https://travis-ci.org/wtsi-hgi/useintest)
[![codecov.io](https://codecov.io/gh/wtsi-hgi/useintest/graph/badge.svg)](https://codecov.io/github/wtsi-hgi/useintest)
[![Documentation Status](https://readthedocs.org/projects/useintest/badge/?version=latest)](http://useintest.readthedocs.io/en/latest/?badge=latest)
# Use In Test
*I don't care how it's done, I just want to use it in my tests!*

[Less blurb, more documentation - link to ReadTheDocs](https://useintest.readthedocs.io).

## Key Features
- Simple way of running services (e.g. Mongo, CouchDB, iRODS) and using executables (e.g. Samtools, icommands).
- No knowledge of containers required.
- No knowledge of service/executables required (how to install it, when it's ready to use, etc.).
- Does not require the installation of anything on your local machine, aside from Docker.
- Makes it simple to test against multiple versions of the same service or set of executables.
- Easy to achieve test isolation.

## Predefined Support
Out of the box support for:

- Mongo
- CouchDB
- iRODS
- Samtools
- GitLab
- Gogs
- Bissell
- Consul

## Why Use This Library?
Software no longer works in isolation; with the trend towards microservices over monoliths, modern day applications 
rely on numerous external services for both data and computation.

Mocks can be a quick way to test against something that (should) behave like the external service that your 
application uses. However, unless a well respected mocking framework exists, the mock you'll end up with will probably 
make the same bad assumptions about the behaviour of service as your faulty code does!

Testing with the "real thing" or a shared dev mirror of it is probably not a good idea during development, 
particularly if the services that you're using hold state. You want to be able to run the tests in parallel, have 
repeatability and have availability, be it for when you're offline or for collaborators outside of your organisation. 
You also want to be able to wipe the slate clean and start again if something goes terribly wrong! It is unlikely you 
will be able to do this in any kind of shared environment.

This library offers a way to just start up services and then throw them away after each test case, with no mess left 
over on your machine. It gives complete test isolation along with confidence that you're testing with services similar 
to those used in production.


## Quick Examples
Start up a containerised instance of Mongo:
```python
from useintest.predefined.mongo import MongoServiceController

# Starts a containerised version of Mongo
controller = MongoServiceController()              
with controller.start_service() as service:      
    run_my_tests(my_application, service.host, service.port)
```

Use samtools in a container from the host machine via "proxy executables":
```python
from useintest.predefined.samtools import SamtoolsExecutablesController

controller = SamtoolsExecutablesController()  
executables_directory = controller.write_executables()
# In the case of Samtools, there will be one executable in `executables_directory` named "samtools"
run_my_tests(my_application, executables_directory)
controller.tear_down()
```


## Documentation
For more details, including information on how to setup and use the library, please [view the documentation on 
ReadTheDocs](https://useintest.readthedocs.io) or read it from `/docs`.


