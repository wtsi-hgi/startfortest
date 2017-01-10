# Development
## Setup
Install both library dependencies and the dependencies needed for testing:
```bash
$ pip3 install -q -r requirements.txt
$ pip3 install -q -r test_requirements.txt
```

## Testing
Using nosetests, in the project directory, run:
```bash
$ nosetests -v --exclude-test=useintest.tests.services._common.TestDockerisedServiceControllerSubclass --exclude-test=useintest.tests.services._common.create_tests
```

To generate a test coverage report with nosetests, add the flags:
```
--with-coverage --cover-package=useintest --cover-inclusive 
```

## Documentation
The documentation can be served using [mkdocs](http://www.mkdocs.org/) and then viewed through a web browser. After 
[installing mkdocs](http://www.mkdocs.org/#installation), setup from the project root directory using:
```bash
$ mkdocs serve
```