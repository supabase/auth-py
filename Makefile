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

sync_infra:
	python scripts/gh-download.py --repo=supabase/gotrue-js --branch=master --folder=infra

run_tests: run_infra sleep tests

build_sync:
	poetry run unasync supabase_auth tests

build_run_tests: build_sync run_tests
	echo "Done"

sleep:
	sleep 20

rename_project: rename_package_dir rename_package

rename_package_dir:
	mv supabase_auth gotrue

rename_package:
	sed -i 's/supabase_auth/gotrue/g' pyproject.toml tests/_async/clients.py tests/_sync/clients.py tests/_async/test_gotrue_admin_api.py tests/_sync/test_gotrue_admin_api.py tests/_async/test_utils.py tests/_sync/test_utils.py tests/_async/utils.py tests/_sync/utils.py README.md

build_package:
	poetry build
