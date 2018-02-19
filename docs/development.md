# Development
## Setup
Install both the library's dependencies (for all modules) and the dependencies needed for testing:
```bash
find . -name requirements.txt -exec pip install --disable-pip-version-check -r "{}" \;
pip install -q -r test_requirements.txt
```

## Testing
In the project directory, run:
```bash
PYTHONPATH=. python -m unittest discover -v -s useintest/tests
```
To test only the latest configuration of each module set: `TEST_LATEST_ONLY=1`.


## Documentation
The documentation can be served using [mkdocs](http://www.mkdocs.org/) and then viewed through a web browser. After 
[installing mkdocs](http://www.mkdocs.org/#installation), setup from the project root directory using:
```bash
$ mkdocs serve
```
