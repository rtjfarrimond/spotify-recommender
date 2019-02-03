###############################################################################
# Build instructions
###############################################################################

ci: init build-all test-all check-style

build-all: build-crawler build-extractor

build-crawler: delete-cache
	docker build --force-rm=true -t spotify-crawler ./crawler

build-extractor: init
	docker build --force-rm=true -t feature-extractor ./feature-extractor


###############################################################################
# Test instructions
###############################################################################

test-all: test-crawler test-feature-extractor

test-crawler: delete-cache
	docker-compose run --rm test-crawler

test-feature-extractor: init

check-style: init
	docker-compose run --rm --entrypoint 'flake8 --extend-ignore=W391 /usr/local/src/app' crawler


###############################################################################
# Run instructions
###############################################################################

crawl: delete-cache
	docker-compose run --rm crawler

extract: init
	docker-compose run --rm feature-extractor


###############################################################################
# Other
###############################################################################

delete-cache: init
	find . -name __pycache__ | sudo xargs rm -rf
	rm -f crawler/app/.cache* || exit 0

clean: init
	sudo rm -rf crawler/app/audio || exit 0

init:
	set -ex
