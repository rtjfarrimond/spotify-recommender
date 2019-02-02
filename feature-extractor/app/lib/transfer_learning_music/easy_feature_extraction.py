import sys
from argparse import Namespace
import librosa
from keras import backend as K
from models_transfer import build_convnet_model
import numpy as np
import keras
import kapre
import multiprocessing
import os
import boto3


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
    args = Namespace(test=False, data_percent=100, model_name='', tf_type='melgram',
                     normalize='no', decibel=True, fmin=0.0, fmax=6000,
                     n_mels=96, trainable_fb=False, trainable_kernel=False,
                     conv_until=mid_idx)
    model = build_convnet_model(args, last_layer=False)
    model.load_weights('weights_transfer/weights_layer{}_{}.hdf5'.format(mid_idx, K._backend),
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
        audio_path_local = '{}{}'.format(AUDIO_ROOT, os.path.basename(audio_path))

        # Download the file
        try:
            client.download_file(bucket, audio_path, audio_path_local)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise

    if from_aws:
       src, sr = librosa.load(audio_path_local, offset=offset, sr=SR, duration=LEN_SRC)
    else:
        src, sr = librosa.load(audio_path, offset=offset, sr=SR, duration=LEN_SRC)
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
    print('Loading/extracting {}...'.format(audio_path))
    src = load_audio(audio_path, IS_AWS_FILE)
    features = [models[i].predict(src)[0] for i in range(5)]
    return np.concatenate(features, axis=0)

def gen_temp_file_name(f_path, n):
    return TEMP_DIR+str(n)+'_'+os.path.basename(f_path)

def save_intermittent(f_path, features, n):
    if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)

    np.save(gen_temp_file_name(f_path, n), features)
    print('Saved first {} features.'.format(n))

    if n > N_INTERMITTENT:
        os.remove(gen_temp_file_name(f_path, n-N_INTERMITTENT))

def empty_safe_concat_array(could_be_empty, to_concat):
    if np.array_equal(could_be_empty, np.array([])):
        return np.array(to_concat, dtype=np.float32)
    else:
        return np.concatenate(
            [could_be_empty, np.array(to_concat, dtype=np.float32)])

def predict_cpu(f_path, models, n_jobs):
    """Predict features with multiprocessing
    path_line: string, path + '\n'
    models: five models for each layer
    """
    pool = multiprocessing.Pool(processes=n_jobs)
    paths = f_path.readlines()

    ret = np.array([])

    lines_left = len(paths)
    i = 0
    while lines_left > N_INTERMITTENT:
        next_paths = paths[i:i+N_INTERMITTENT]
        arg_gen = _paths_models_generator(next_paths, models)
        features = pool.map(_predict_one, arg_gen)
        ret = empty_safe_concat_array(ret, features)

        save_intermittent(out_path, ret, i+N_INTERMITTENT)

        lines_left -= N_INTERMITTENT
        i += N_INTERMITTENT

    arg_gen = _paths_models_generator(paths[i:], models)
    features = pool.map(_predict_one, arg_gen)
    return empty_safe_concat_array(ret, features)


def main(txt_path, out_path, n_jobs=1):
    models = [load_model(mid_idx) for mid_idx in range(5)]  # for five models...
    all_features = []
    with open(txt_path) as f_path:
        all_features = predict_cpu(f_path, models, n_jobs)

    print('Saving all features at {}..'.format(out_path))
    np.save(out_path, all_features)
    print('Done. Saved a numpy array size of (%d, %d)' % all_features.shape)

    # Clean up temp files
    if os.path.exists(TEMP_DIR):
        for f in os.listdir(TEMP_DIR):
            os.remove(TEMP_DIR+f)

def warning():
    print('-' * 65)
    print('  * Python 2.7-ish')
    print('  * Keras 1.2.2,')
    print('  * Kapre old one (git checkout a3bde3e, see README)')
    print("  * Read README.md. Come on, it's short..")
    print('')
    print('   Usage: set path file, numpy file, and n_jobs >= 1')
    print('$ python easy_feature_extraction.py audio_paths.txt features.npy 8')
    print('')
    print('    , where audio_path.txt is for paths audio line-by-line')
    print('    and features.npy is the path to store result feature array.')
    print('')
    print('    N.B. If audio is hosted in s3 buckets, include "AWS"')
    print('    in the filename for audio_path.txt, i.e. audio_path_AWS.txt')
    print('-' * 65)


if __name__ == '__main__':
    warning()

    txt_path = sys.argv[1]
    out_path = sys.argv[2]
    n_jobs = int(sys.argv[3])

    if 'AWS' in txt_path:
        IS_AWS_FILE = True

    main(txt_path, out_path, n_jobs)
