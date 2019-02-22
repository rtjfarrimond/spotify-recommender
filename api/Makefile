init:
	set -ex

freeze: init
	pip freeze > api/requirements.txt

test: init
	$(shell . venv/bin/activate)
	python -m unittest discover
