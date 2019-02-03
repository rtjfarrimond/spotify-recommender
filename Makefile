###############################################################################
# Build instructions
###############################################################################

ci: init build-all test-all style-all

build-all: build-crawler build-extractor

build-crawler: delete-cache
	docker build --force-rm=true -t spotify-crawler ./crawler

build-extractor: init
	docker build --force-rm=true -t feature-extractor ./extractor


###############################################################################
# Test instructions
###############################################################################

test-all: test-crawler test-extractor

test-crawler: delete-cache
	docker-compose run --rm test-crawler

test-extractor: init

###############################################################################
# Style instructions
###############################################################################

style-all: style-crawler style-extractor

style-crawler: init
	docker-compose run --rm --entrypoint 'flake8 --extend-ignore=W391 /usr/local/src/app' crawler

style-extractor: init
	docker-compose run --rm --entrypoint 'flake8 --exclude=core/* --extend-ignore=W391 /usr/local/src/app' extractor


###############################################################################
# Run instructions
###############################################################################

crawl: delete-cache
	docker-compose run --rm crawler

extract: init
	docker-compose run --rm extractor


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
