from argparse import Namespace
from core.models_transfer import build_convnet_model
from keras import backend as K
import numpy as np
import boto3
import keras
import librosa
import logging
import multiprocessing
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TEMP_DIR = '/project/features/temp/'
AUDIO_ROOT = '/project/audio/'
IS_AWS_FILE = False
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


def load_audio(audio_path, from_aws):
    offset = 0

    """Load audio file, shape it and return"""
    if from_aws:
        offset = 90
        # Set up aws client
        bucket = os.environ['SYNCH_MP3_S3_DELIVERY_BUCKET_NAME']
        client = boto3.client(
            's3',
            aws_access_key_id=os.environ['SYNCH_MP3_UPLOAD_ACCESS_KEY'],
            aws_secret_access_key=os.environ['SYNCH_MP3_UPLOAD_SECRET_KEY'])

        # Define local audio_path
        audio_path_local = '{}{}'.format(
            AUDIO_ROOT,
            os.path.basename(audio_path))

        # Download the file
        client.download_file(bucket, audio_path, audio_path_local)
        # try:
        #     client.download_file(bucket, audio_path, audio_path_local)
        # except botocore.exceptions.ClientError as e:
        #     if e.response['Error']['Code'] == "404":
        #         logger.warn("The object does not exist.")
        #     else:
        #         raise

    if from_aws:
        src, sr = librosa.load(
            audio_path_local, offset=offset, sr=SR, duration=LEN_SRC)
    else:
        src, sr = librosa.load(
            audio_path, offset=offset, sr=SR, duration=LEN_SRC)
    len_src = len(src)
    if len_src < ref_n_src:
        new_src = np.zeros(ref_n_src)
        new_src[:len_src] = src
        return new_src[np.newaxis, np.newaxis, :]
    else:
        return src[np.newaxis, np.newaxis, :ref_n_src]

    if from_aws:
        os.remove(audio_path_local)


def _paths_models_generator(lines, models):
    for line in lines:
        yield (line.rstrip('\n'), models)


def _predict_one(args):
    """target function in pool.map()"""
    line, models = args
    audio_path = line.rstrip('\n')
    logger.info('Loading/extracting {}...'.format(audio_path))
    src = load_audio(audio_path, IS_AWS_FILE)
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


def main(f_path, out_path, n_jobs=1):
    logger.info("Extracting features from audio file at " + f_path + "...")
    models = [load_model(mid_idx) for mid_idx in range(5)]
    all_features = predict_cpu(f_path, models, n_jobs)

    logger.info('Saving all features at {}..'.format(out_path))
    dir_name = os.path.dirname(out_path)
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    np.save(out_path, all_features)
    logger.info(
        'Done. Saved a numpy array size of (%d, %d)' % all_features.shape)

    # Clean up temp files
    if os.path.exists(TEMP_DIR):
        for f in os.listdir(TEMP_DIR):
            os.remove(TEMP_DIR+f)


if __name__ == '__main__':
    audio_path = os.getenv("AUDIO_PATH", "")
    out_path = os.getenv("OUT_PATH", "")

    if not audio_path or audio_path == "":
        raise ValueError("Path to audio file not set.")

    if not out_path or out_path == "":
        raise ValueError("Path to write features out not set.")

    if not os.path.isfile(audio_path):
        raise ValueError(
            "File " + audio_path + "does not exist or is not a regular file.")

    main(audio_path, out_path)
