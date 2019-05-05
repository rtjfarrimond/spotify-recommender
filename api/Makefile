ITEM_CACHE_PATH = /tmp/item_cache.pkl
export TRACKS_TABLE = spot-rec-audio-metadata
export DYNAMO_ANNOY_INDEX_NAME = annoy_index
export ANNOY_BUCKET_NAME = spot-rec-annoy-bucket
export ANNOY_FILE_NAME = annoy.ann


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
