

build:
	docker-compose build

crawl: init
	rm crawler/app/.cache* || exit 0
	docker-compose run --rm crawler

init:
	set -ex
