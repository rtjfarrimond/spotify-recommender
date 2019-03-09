_SYSTEM_CODE = spot-rec

AUDIO_BUCKET_NAME = spot-rec-audio-upload-bucket
CRAWLER_IMAGE_NAME = spotify-crawler
EXTRACTOR_IMAGE_NAME = feature-extractor
GET_LAMBDA_BUCKET = spot-rec-lambda-bucket
AWS_DEFAULT_REGION = eu-west-1
AWS_REGION ?= eu-west-1
CONFIG_FILE_DIR = config
EXTRACTOR_ENV_NAME = .env.extractor

SSM_FETCH = aws ssm get-parameter --output text --with-decryption --query 'Parameter.Value' --region $(AWS_DEFAULT_REGION) --name

EXTRACTOR_ECR_REPO = $(shell $(SSM_FETCH) /$(_SYSTEM_CODE)/extractor_ecr_repo)
EXTRACTOR_ECR_IMAGE_NAME = ${AWS_ACCOUNT_ID}.dkr.ecr.$(AWS_REGION).amazonaws.com/$(EXTRACTOR_ECR_REPO)

###############################################################################
# Build instructions
###############################################################################

ci: init build-all test-all test-api-ci style-all save-extractor

build-all: build-crawler build-extractor

build-crawler: delete-cache
	docker build --force-rm=true -t $(CRAWLER_IMAGE_NAME) ./crawler

build-extractor: init
	docker build --force-rm=true -t $(EXTRACTOR_IMAGE_NAME) ./extractor

###############################################################################
# Deploy instructions
###############################################################################

tag-extractor: init
	docker tag $(EXTRACTOR_IMAGE_NAME) $(EXTRACTOR_ECR_IMAGE_NAME)

# Used to save between CircleCI build and deploy phases.
save-extractor: init tag-extractor
	mkdir docker-image
	docker save -o docker-image/image.tar $(EXTRACTOR_ECR_IMAGE_NAME)

# Used to load image in CircleCI deployment phase.
load-extractor: init
	docker load --input workspace/docker-image/image.tar

push-extractor: init ecr-login load-extractor
	$(aws ecr get-login --no-include-email)
	docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/$(EXTRACTOR_ECR_REPO)

###############################################################################
# Test instructions
###############################################################################

# Currently does not run test-api as does not work in ci.
# TODO: set up api proejct with pipenv for Circle CI to work properly.
test-all: test-crawler test-extractor test-api-ci

test-all-local: test-crawler test-extractor test-api-local

test-crawler: delete-cache
	docker-compose run --rm test-crawler

test-extractor: delete-cache

test-api-local: delete-cache
	$(MAKE) -C api/ test-local

test-api-ci: delete-cache
	$(MAKE) -C api/ test-ci

###############################################################################
# Style instructions
###############################################################################

style-all: style-crawler style-extractor

style-crawler: init
	docker-compose run --rm --entrypoint 'flake8 --extend-ignore=W391 /usr/local/src/app' crawler

style-extractor: init
	docker-compose run --rm --entrypoint 'flake8 --exclude=core/* --extend-ignore=W391 /usr/local/src/app' extractor


###############################################################################
# Config instructions
###############################################################################

config-extractor: init
	@echo 'S3_BUCKET_NAME=$(shell $(SSM_FETCH) /$(_SYSTEM_CODE)/audio_bucket_name)' > $(CONFIG_FILE_DIR)/$(EXTRACTOR_ENV_NAME)
	@echo 'DYNAMODB_TABLE=$(shell $(SSM_FETCH) /$(_SYSTEM_CODE)/dynamodb_table)' >> $(CONFIG_FILE_DIR)/$(EXTRACTOR_ENV_NAME)

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

clean: init
	aws s3 rm s3://$(AUDIO_BUCKET_NAME) --recursive --exclude "terraform.tfstate"

init:
	set -ex
	sudo pip install --upgrade pip
	sudo pip install awscli

