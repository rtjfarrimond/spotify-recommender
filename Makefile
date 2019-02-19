AUDIO_BUCKET_NAME=spotify-recommender-bucket
CRAWLER_IMAGE_NAME=spotify-crawler
EXTRACTOR_IMAGE_NAME=feature-extractor
EXTRACTOR_ECR_REPO=spot-rec-feature-extractor
GET_LAMBDA_BUCKET=spot-rec-lambda-bucket
GET_VERSION=v0.1.1


###############################################################################
# Build instructions
###############################################################################

ci: init build-all test-all style-all

build-all: build-crawler build-extractor

build-crawler: delete-cache
	docker build --force-rm=true -t $(CRAWLER_IMAGE_NAME) ./crawler

build-extractor: init
	docker build --force-rm=true -t $(EXTRACTOR_IMAGE_NAME) ./extractor

## Not yet used in CI/CD
tag-extractor: init
	docker tag $(EXTRACTOR_IMAGE_NAME) ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/$(EXTRACTOR_ECR_REPO)

push-extractor: ecr-login
	docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/$(EXTRACTOR_ECR_REPO)

ecr-login: init
	$(aws ecr get-login --no-include-email)

###############################################################################
# Deploy instructions
###############################################################################

get-lambda: init
	cp get-handler/main.py .
	zip get-handler.zip main.py
	aws s3 cp get-handler.zip s3://$(GET_LAMBDA_BUCKET)/$(GET_VERSION)/get-handler.zip
	rm -f get-handler.zip main.py

###############################################################################
# Test instructions
###############################################################################

test-all: test-crawler test-extractor

test-crawler: delete-cache
	docker-compose run --rm test-crawler

test-extractor: delete-cache

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
	aws s3 rm s3://$(AUDIO_BUCKET_NAME) --recursive --exclude "terraform.tfstate"

init:
	set -ex

