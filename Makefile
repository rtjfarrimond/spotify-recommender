

test-crawler: delete-cache
	docker-compose run --rm crawler-tests

build-all: build-crawler

build-crawler: init
	docker build -t spotify-crawler ./crawler

crawl: delete-cache
	docker-compose run --rm crawler

delete-cache: init
	rm crawler/app/.cache* || exit 0

init:
	set -ex
