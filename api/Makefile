init:
	set -ex
	$(shell . venv/bin/activate)

freeze: init
	pip freeze > api/requirements.txt

test: init
	python -m unittest discover
