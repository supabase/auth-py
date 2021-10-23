build_sync:
	poetry run unasync gotrue tests

install:
	poetry install

tests: install tests_only tests_pre_commit
	echo "Done"

tests_pre_commit:
	poetry run pre-commit run --all-files

tests_only:
	poetry run pytest --cov=./ --cov-report=xml -vv

run_infra:
	cd infra &&\
	docker-compose down &&\
	docker-compose up -d

build_run_tests: build_sync run_infra tests
	echo "Done"
