install:
	poetry install

install_poetry:
	curl -sSL https://install.python-poetry.org | python -
	sudo rm -r .venv
	poetry install

tests: install tests_only tests_pre_commit

tests_pre_commit:
	poetry run pre-commit run --all-files

tests_only:
	poetry run pytest --cov=./ --cov-report=xml --cov-report=html -vv

run_infra:
	cd infra &&\
	docker-compose down &&\
	docker-compose up -d

run_tests: run_infra tests

build_sync:
	poetry run unasync gotrue tests

build_run_tests: build_sync run_tests
	echo "Done"
