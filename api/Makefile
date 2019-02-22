init:
	set -ex

freeze: init
	pip freeze > api/requirements.txt

test-local: init
	$(shell . venv/bin/activate)
	python -m unittest discover

test-ci: init
	pipenv run python -m unittest discover
