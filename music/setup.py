"""Download necessary files for the project"""
import os

import requests

DEPENDENCIES = {
    "exploded_song_df.csv": "https://dl.dropboxusercontent.com/scl/fi/0c9cs5rv55xcp22eyhzhn/exploded_song_df.csv?rlkey=rlpita1lom7tsnen3om3fq60k&e=1&dl=1",
    "inverse_index.json": "https://dl.dropboxusercontent.com/scl/fi/kmse8cun8b7wkv7pkbty2/inverse_index.json?rlkey=069eenxc00wads0227i6b35ug&e=1&dl=1",
}


def download(url: str, local_path: str):
    """Download file from url to specified path"""
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading from {url}: {e}")
        return
    with open(local_path, "wb") as f:
        f.write(response.content)


def setup():
    """Download all necessary files"""
    for fname, url in DEPENDENCIES.items():
        if os.path.exists(f"music/{fname}"):
            print(f"{fname} already exists")
        else:
            print(f"Downloading {fname}...")
            download(url, f"music/{fname}")

    print("Setup complete\n")


if __name__ == "__main__":
    setup()
