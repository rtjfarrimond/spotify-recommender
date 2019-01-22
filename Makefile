

build-all: build-crawler

build-crawler: init
	docker build -t spotify-crawler ./crawler

test-all: test-crawler

test-crawler: delete-cache
	docker-compose run --rm test-crawler

check-style: init
	docker-compose run --rm --entrypoint 'flake8 --extend-ignore=W391 /usr/local/src/app' crawler

crawl: delete-cache
	docker-compose run --rm crawler

delete-cache: init
	rm -f crawler/app/.cache* || exit 0

clean: init
	sudo rm -rf crawler/app/audio

init:
	set -ex
