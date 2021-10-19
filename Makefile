build_sync:
	if [ -d "build" ]; then rm -r "build"; fi
	python build_sync.py build
	if [ -d "gotrue/_sync" ]; then rm -r "gotrue/_sync"; fi
	if [ -d "tests/_sync" ]; then rm -r "tests/_sync"; fi
	cp -r "build/lib/gotrue/_sync" "gotrue/_sync"
	cp -r "build/lib/tests/_sync" "tests/_sync"
	rm -r "build"

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
