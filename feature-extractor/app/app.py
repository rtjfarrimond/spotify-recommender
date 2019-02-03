from __future__ import print_function
import os


if __name__ == '__main__':
    audio_path = os.getenv("AUDIO_PATH", "")

    if not audio_path or audio_path == "":
        raise ValueError("Path to audio file not set.")

    if not os.path.isfile(audio_path):
        raise ValueError(
            "File " + audio_path + "does not exist or is not a regular file.")

    print(audio_path)
