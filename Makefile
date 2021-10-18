build_sync:
	if [ -d "build" ]; then rm -r "build"; fi
	python build_sync.py build
	if [ -d "gotrue/_sync" ]; then rm -r "gotrue/_sync"; fi
	cp -r "build/lib/gotrue/_sync" "gotrue/_sync"
	rm -r "build"

install:
	poetry install

tests: install
	poetry run pre-commit run --all-files
	poetry run pytest --cov=./ --cov-report=xml -sx
