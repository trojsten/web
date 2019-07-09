Trojsten web
===

Trojstenovy web

[![CircleCI](https://circleci.com/gh/trojsten/web.svg?style=svg)](https://circleci.com/gh/trojsten/web)
[![codecov](https://codecov.io/gh/trojsten/web/branch/master/graph/badge.svg?token=t4kSkwFccG)](https://codecov.io/gh/trojsten/web)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

## Getting started

This project uses [pre-commit](https://pre-commit.com/). 
You can install it using `pip install pre-commit` and it's also included in [the project requirements](https://github.com/trojsten/web/blob/master/requirements.txt).

Activate it with 
```bash
pre-commit install --allow-missing-config
```

### Running locally

Please follow the installation manual here: https://github.com/trojsten/web/wiki/Návod-na-inštaláciu

### Committing code

Please send a pull request with a descriptive title and all necessary information in the description. Preferably all in English.
The pull request needs to pass automatic checks and have at least one approval from the project maintainers.

We currently check following things:
- code style
  - the code must follow [black](https://github.com/python/black) codestyle. The easiest way to achieve this is automatically format with the `black` tool. This is also enforced by the pre-commit check. Note that black is currently not included in the project requirements, because it requires Python 3.6+.
  - imports must be sorted alphabetically (within import categories). You can use [`isort`](https://github.com/timothycrosley/isort) to automatically sort imports the correct way. This is also enforced by the pre-commit check.
  - the code must also pass [`flake8`](http://flake8.pycqa.org/en/latest/) lint check.
- tests
  - the PR must pass all tests
  - the PR should also have a sufficent code coverage.
- migrations
  - the PR must include all necessary migrations. Note that Django localizes migrations, so make sure your translations are up to date (`./manage.py compilemessages`) before generating migrations.

## Sites running on this:
- https://ksp.sk
- https://prask.ksp.sk
- https://fks.sk
- https://ufo.fks.sk
- https://fx.fks.sk
- https://kms.sk
- https://wiki.trojsten.sk
- https://login.trojsten.sk

## Related projects
- https://github.com/koniiiik/ksp_login
- https://github.com/trojsten/news
- https://github.com/trojsten/django-tips
- https://github.com/trojsten/submit
