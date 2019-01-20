# Music Recommender
The purpose of this application is...

It consists of the following components:


## Web crawler:
* Crawls Spotify playlists, gets the 30s preview URL, downloads audio to S3.
* Uses the [Spotify web API](https://developer.spotify.com/documentation/web-api/quick-start/).

### To do
* Check the legality of this...


## Infrastructure:
* An S3 bucket to temporarily store audio from which to extract features.


## Feature extractor:
* Triggered by event from audio file uploaded to S3.
* Pulls audio file down, extracts features, stores them in database.
* Deletes the audio when done.
  * Investigate whether this can be done by streaming, rather than dl.


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
