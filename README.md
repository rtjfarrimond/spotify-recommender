[![CircleCI](https://circleci.com/gh/rtjfarrimond/spotify-recommender/tree/master.svg?style=svg&circle-token=39f17eb33b9e384bec4d842213c7e2c6a3b29693)](https://circleci.com/gh/rtjfarrimond/spotify-recommender/tree/master)

# Spotify Recommender
This application provides the services needed to perform content based music
recomendation using features extracted from 30s track previews available via
the [Spotify Web API](https://developer.spotify.com/documentation/web-api/).

# Dependencies
* [Hashicorp Terraform v0.11.11](https://www.terraform.io/)
* [Serverless v1.37.1](https://serverless.com/)
* [Serverless Python Requirements v4.3.0](https://www.npmjs.com/package/serverless-python-requirements)

# Components
## Playlist crawler:
* Crawls Spotify playlists, gets the 30s preview URL, downloads audio to S3.
* Uses the [Spotify web API](https://developer.spotify.com/documentation/web-api/quick-start/).

## Feature extractor:
* Uses [Keunwoo Choi's CNN](https://github.com/keunwoochoi/transfer_learning_music)
  for feature extraction.
* Triggered by event from audio file uploaded to S3.
    * Pulls audio file down, extracts features, stores them in database.
    * Deletes the audio when done.

## Database:
* For storage and retrieval of unprocessed features extracted from audio files.
* The `AnnoyIndex` item attribute is computed as a uuid1, bit shifted 114 bits
  to the right. This ensures that the python int maps within the C 32 bit length
  limit, whilst remaining unique, as the 14 rightmost bits are generated from the
  time that the uuid is generated. See [the documentation](https://docs.python.org/2/library/uuid.html#uuid.uuid1) for more details.

## API:
* Provide a GET endpoint to service recommendations following query by example.
* Uses [ANNOY](https://github.com/spotify/annoy), to service queries.
* Takes a single parameter, a spotify track ID.
* Subscribes to events that notify when the ANNOY space has been updated.

## ANNOY service
This service is the custodian of the ANNOY space. It is responsible for:
* Initialising the annoy space and storing it in S3.
* Updating the annoy space following writes to the database.
  * Possibly implemented by subscribing to a DynamoDB event stream.
* Publishing events to let subscribers know when the annoy space has been updated.
  * Possibly implemented by an event triggered via upload to the S3 bucket.

## Infrastructure:
* An S3 bucket to temporarily store audio from which to extract features.
* An AWS managed database instance in which to store extracted features.

# Getting started

1. The services use `.env` files for configuration, which must be created and
   stored in the `config/` directory. In this directory you will also find
   templates to create the necessary `.env` files.

1. To build the project, run:

        make build-all

1. To run the playlist crawler, run:

        make crawl

2. To run the feature extractor, run:

        make extract

