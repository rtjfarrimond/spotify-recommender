from __future__ import print_function
from argparse import Namespace
from core.models_transfer import build_convnet_model
from keras import backend as K
from zipfile import ZipFile
import numpy as np
import boto3
import glob
import keras
import librosa
import logging
import multiprocessing
import os
import settings


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


def _paths_models_generator(lines, models):
    for line in lines:
        yield (line.rstrip('\n'), models)


def _predict_one(args):
    """target function in pool.map()"""
    line, models = args
    audio_path = line.rstrip('\n')
    src = load_audio(audio_path)
    features = [models[i].predict(src)[0] for i in range(5)]
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


def predict_cpu(f_path, models, n_jobs):
    """ Predict features with multiprocessing.

    Parameters:
    -----------
    f_path:
        string, path to the input audio file.

    models:
        list of keras models to use for feature extraction.

    n_jobs:
        int, number of threads to use.

    Returns:
    --------
        numpy.array, features extracted.
    """
    pool = multiprocessing.Pool(processes=n_jobs)
    paths = [f_path]
    ret = np.array([])

    arg_gen = _paths_models_generator(paths[:], models)
    features = pool.map(_predict_one, arg_gen)
    return empty_safe_concat_array(ret, features)


def main(paths, out_path, n_jobs=1):
    models = [load_model(mid_idx) for mid_idx in range(5)]
    count = 1
    for f_path in paths:
        logger.info("Extracting features from track {} of {}...".format(
                    count, len(paths)))
        count += 1
        all_features = predict_cpu(f_path, models, n_jobs)

        logger.info('Saving features at {}..'.format(out_path))
        feat_name = os.path.basename(f_path).replace('mp3', 'npy')
        feat_path = "{}/{}".format(out_path, feat_name)
        np.save(feat_path, all_features)
        logger.info(
            'Done. Saved a numpy array size of (%d, %d)' % all_features.shape)

        # Clean up temp files
        if os.path.exists(TEMP_DIR):
            for f in os.listdir(TEMP_DIR):
                os.remove(TEMP_DIR+f)


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


if __name__ == '__main__':
    DYNAMODB_TABLE = settings.DYNAMODB_TABLE
    S3_BUCKET_NAME = settings.S3_BUCKET_NAME
    ZIP_FILE_NAME = settings.ZIP_FILE_NAME

    if not DYNAMODB_TABLE:
        logger.critical("DynamoDB table not configured, cannot continue!")
        exit(1)

    if not S3_BUCKET_NAME:
        logger.critical("S3 bucket name not configured, cannot continue!")
        exit(1)

    if not ZIP_FILE_NAME:
        logger.critical("Zip file name not configured, cannot continue!")
        exit(1)

    audio_path = '/tmp'
    feature_path = '/tmp/features'
    if not os.path.exists(feature_path):
        logger.info("Creating dir {}...".format(feature_path))
        os.mkdir(feature_path)
    download_extract_zip(S3_BUCKET_NAME, ZIP_FILE_NAME, dir_name=audio_path)

    paths = glob.glob('{}/**/*.mp3'.format(audio_path))

    # Extract audio features
    # main(paths, feature_path)
    main(paths[:1], feature_path)
    print(os.listdir(feature_path))
