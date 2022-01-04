install:
	poetry install

install_poetry:
	curl -sSL https://install.python-poetry.org | python -

tests: install tests_only tests_pre_commit

tests_pre_commit:
	poetry run pre-commit run --all-files

tests_only:
	poetry run pytest --cov=./ --cov-report=xml --cov-report=html -vv

run_infra:
	cd infra &&\
	docker-compose down &&\
	docker-compose up -d

clean_infra:
	cd infra &&\
	docker-compose down --remove-orphans &&\
	docker system prune -a --volumes -f

run_tests: run_infra sleep tests

build_sync:
	poetry run unasync gotrue tests

build_run_tests: build_sync run_tests
	echo "Done"

sleep:
	sleep 20
