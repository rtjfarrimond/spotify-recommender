[![CircleCI](https://circleci.com/gh/rtjfarrimond/spotify-recommender/tree/master.svg?style=svg&circle-token=39f17eb33b9e384bec4d842213c7e2c6a3b29693)](https://circleci.com/gh/rtjfarrimond/spotify-recommender/tree/master)

# Spotify Recommender
The purpose of this application is to provide content based music
recomendation using features extracted from 30s track previews available via
the [Spotify Web API](https://developer.spotify.com/documentation/web-api/).

## Getting started

1. The services use `.env` files for configuration, which must be created and
   stored in the `config/` directory. In this directory you will also find
   templates to create the necessary `.env` files.

1. To build the project, run:

        make build-all

1. To run the playlist crawler, run:

        make crawl

# Components
The application consists of the following components:


## Playlist crawler:
* Crawls Spotify playlists, gets the 30s preview URL, downloads audio to S3.
* Uses the [Spotify web API](https://developer.spotify.com/documentation/web-api/quick-start/).

### To do
* Fix spotipy token authorisation.
* Write to s3 bucket.


## Infrastructure:
* An S3 bucket to temporarily store audio from which to extract features.
* An AWS managed database instance in which to store extracted features.


## Feature extractor:
* Uses [Keunwoo Choi's CNN](https://github.com/keunwoochoi/transfer_learning_music)
  for feature extraction.
* Triggered by event from audio file uploaded to S3.
* Pulls audio file down, extracts features, stores them in database.
* Deletes the audio when done.
  * Investigate whether this can be done by streaming, rather than dl.

### To do:
* Switch to use python alpine base image

## Database:
* For storage and retrieval of unprocessed features extracted from audio files.

### To do
* Consider which type of database needed (kv store is first instinct)
  * Choose a specific technology that conforms to this type


## API:
* Provides a recommendation service following a query by example paradigm.
* Uses ANNOY to service queries.
* Accepts queries that provide a URL or unique identifier that maps to a Spotify track.


## Still to consider
* When do we create the ANNOY space?
