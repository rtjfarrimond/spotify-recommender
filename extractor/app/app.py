from __future__ import print_function
from argparse import Namespace
from boto3.dynamodb.types import Binary
from core.models_transfer import build_convnet_model
from functools import partial
from keras import backend as K
from zipfile import ZipFile
import numpy as np
import boto3
import glob
import json
import keras
import librosa
import logging
import os
import pickle
import settings
import uuid


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TEMP_DIR = '/project/features/temp/'
N_INTERMITTENT = 100
SR = 12000  # [Hz]
LEN_SRC = 29.  # [second]
ref_n_src = 12000 * 29


if keras.__version__[0] != '1':
    raise RuntimeError('Keras version should be 1.x, maybe 1.2.2')


def load_model(mid_idx):
    """Load one model and return it"""
    assert 0 <= mid_idx <= 4
    args = Namespace(
        test=False,
        data_percent=100,
        model_name='',
        tf_type='melgram',
        normalize='no',
        decibel=True,
        fmin=0.0,
        fmax=6000,
        n_mels=96,
        trainable_fb=False,
        trainable_kernel=False,
        conv_until=mid_idx)
    model = build_convnet_model(args, last_layer=False)
    model.load_weights(
        'core/weights_transfer/weights_layer{}_{}.hdf5'.format(
            mid_idx, K._backend),
        by_name=True)

    return model


def load_audio(audio_path):
    offset = 0

    """Load audio file, shape it and return"""
    src, sr = librosa.load(audio_path, offset=offset, sr=SR, duration=LEN_SRC)
    len_src = len(src)
    if len_src < ref_n_src:
        new_src = np.zeros(ref_n_src)
        new_src[:len_src] = src
        return new_src[np.newaxis, np.newaxis, :]
    else:
        return src[np.newaxis, np.newaxis, :ref_n_src]


def _paths_models_generator(lines):
    for line in lines:
        yield (line.rstrip('\n'), MODELS)


def _predict_one(line):
    audio_path = line.rstrip('\n')
    src = load_audio(audio_path)
    features = [MODELS[i].predict(src)[0] for i in range(5)]
    return np.concatenate(features, axis=0)


def gen_temp_file_name(f_path, n):
    return TEMP_DIR+str(n)+'_'+os.path.basename(f_path)


def save_intermittent(f_path, features, n):
    if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)

    np.save(gen_temp_file_name(f_path, n), features)
    logger.info('Saved first {} features.'.format(n))

    if n > N_INTERMITTENT:
        os.remove(gen_temp_file_name(f_path, n-N_INTERMITTENT))


def empty_safe_concat_array(could_be_empty, to_concat):
    if np.array_equal(could_be_empty, np.array([])):
        return np.array(to_concat, dtype=np.float32)
    else:
        return np.concatenate(
            [could_be_empty, np.array(to_concat, dtype=np.float32)])


def extract_features(table_name, region, f_path, track):
    def write_to_db(track, features, table_name, region):
        logger.info(
            "Writing track {} to DynamoDB Table {}...".format(
                track,
                table_name
            )
        )
        track = track['track']
        track_id = track['id']

        # TODO: Pull hash and sort keys from ssm.
        item = {
            "TrackId": track_id,
            "Source": "spotify",
            "AnnoyIndex": int(uuid.uuid1().int >> 114),
            "Title": track['title'],
            "Artists": track['artists'],
            "PreviewUrl": track['preview_url'],
            "Features": Binary(features)
        }
        dynamodb = boto3.resource('dynamodb', region_name=region)
        table = dynamodb.Table(table_name)
        table.put_item(Item=item)

    logger.info(
        "Extracting features for track {}...".format(
            track['track']['id']
        )
    )
    features = _predict_one(f_path)
    pkl_features = pickle.dumps(features, protocol=0)

    write_to_db(track, pkl_features, table_name, region)


def download_extract_zip(bucket, zip_name, dir_name='/tmp'):
    ''' Download a zip from s3 and extract contents to directory.

    Parameters:
    -----------
    bucket:
        string, name of the S3 bucket to fetch from.

    zip_name:
        string, name of the zip file to fetch.

    dir_name:
        string, location to download and extract to, `/tmp` by default.
    '''
    s3 = boto3.resource('s3')
    zip_path = '{}/{}'.format(dir_name, zip_name)
    s3.Bucket(bucket).download_file(zip_name, zip_path)
    zip_file = ZipFile(zip_path, 'r')
    zip_file.extractall(dir_name)
    zip_file.close()


def delete_zip(bucket, zip_name):
    logger.info("Deleting {} from {}...".format(zip_name, bucket))
    s3 = boto3.resource('s3')
    s3.Object(bucket, zip_name).delete()


def parse_tracks_json_lines(json_lines):
    with open(json_lines) as f:
        lines = f.readlines()

    tracks = [json.loads(line.replace(',\n', '')) for line in lines]
    # tracks_nested = {track['track']['id']: track for track in tracks}

    # return tracks_nested
    return tracks


if __name__ == '__main__':
    DYNAMODB_TABLE = settings.DYNAMODB_TABLE
    S3_BUCKET_NAME = settings.S3_BUCKET_NAME
    ZIP_FILE_NAME = settings.ZIP_FILE_NAME
    AWS_DEFAULT_REGION = settings.AWS_DEFAULT_REGION

    if not DYNAMODB_TABLE:
        logger.critical("DynamoDB table not configured, cannot continue!")
        exit(1)

    if not S3_BUCKET_NAME:
        logger.critical("S3 bucket name not configured, cannot continue!")
        exit(1)

    if not ZIP_FILE_NAME:
        logger.critical("Zip file name not configured, cannot continue!")
        exit(1)

    logger.info("DynamoDB table: " + DYNAMODB_TABLE)
    logger.info("S3 bucket name: " + S3_BUCKET_NAME)
    logger.info("Zip file name: " + ZIP_FILE_NAME)

    audio_path = '/tmp'
    feature_path = '/tmp/features'
    if not os.path.exists(feature_path):
        logger.info("Creating dir {}...".format(feature_path))
        os.mkdir(feature_path)

    # Download the zip file.
    download_extract_zip(S3_BUCKET_NAME, ZIP_FILE_NAME, dir_name=audio_path)

    # Load models
    logger.info("Loading models...")
    MODELS = [load_model(mid_idx) for mid_idx in range(5)]

    # Extract audio features
    paths = glob.glob('{}/**/*.mp3'.format(audio_path))
    json_lines = glob.glob('{}/**/*.json'.format(audio_path))[0]
    tracks = parse_tracks_json_lines(json_lines)
    pa_extract = partial(
        extract_features,
        table_name=DYNAMODB_TABLE,
        region=AWS_DEFAULT_REGION
    )

    # Extract and upload features.
    count = 1
    for i in range(len(paths)):
        logger.info(
            "Extracting features for track {} of {}...".format(
                count,
                len(paths)
            )
        )
        count += 1
        pa_extract(f_path=paths[i], track=tracks[i])

    # Delete the zip from s3.
    delete_zip(S3_BUCKET_NAME, ZIP_FILE_NAME)
