ITEM_CACHE_PATH = /tmp/item_cache.pkl

init:
	set -ex

clean: init
	rm -f $(ITEM_CACHE_PATH)

test-local: init clean
	$(shell . venv/bin/activate)
	python -m unittest discover

test-ci: init clean
	pipenv run python -m unittest discover

run: init
	python app.py | jq '.'
