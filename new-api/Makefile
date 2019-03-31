ITEM_CACHE_PATH = /tmp/item_cache.pkl

init:
	set -ex

freeze: init
	$(shell . venv/bin/activate)
	pip freeze -l > api/requirements.txt

test-local: init
	rm -f $(ITEM_CACHE_PATH)
	$(shell . venv/bin/activate)
	python -m unittest discover

test-ci: init
	pipenv run python -m unittest discover
