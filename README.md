# TCF Back-end API


## Tests
### General
In gitlab we are using the `services` to run the dependencies services (Redis, ES) in a containerized environment.
### Running
To run the tests, execute the following command from the root directory:
```bash
coverage run -m pytest -s tests
OR
pytest tests/
```

### Install pre-commit hooks (Linters, formatters, etc.)
```bash
$ pre-commit install
```
And run the hooks on all files (optional), automatically run on every commit:
```bash
$ pre-commit run --all-files
```
