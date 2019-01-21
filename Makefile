

build-all: build-crawler

build-crawler: init
	docker build -t spotify-crawler ./crawler

test-all: test-crawler

test-crawler: delete-cache
	docker-compose run --rm crawler-tests

crawl: delete-cache
	docker-compose run --rm crawler

delete-cache: init
	rm crawler/app/.cache* || exit 0

init:
	set -ex
