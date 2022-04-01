import os
from pathlib import Path
import requests

# pinata is ipfs file management service, they pin any files we are working with
# so they will have our files pinned on their nodes
# thanks to pinata whenever our node goes down, pinata will have all

PINATA_BASE_URL = "https://api.pinata.cloud/"
endpoint = "pinning/pinFileToIPFS"
# above is taken from https://docs.pinata.cloud/api-pinning/pin-file
# Below filepath only applies for bug image, for others you have to change below
filepath = "./img/pug.png"
# below gets the last part "pug.png"
filename = filepath.split("/")[-1:][0]
# below are taken from headers section in https://docs.pinata.cloud/api-pinning/pin-file for post request
headers = {
    "pinata_api_key": os.getenv("PINATA_API_KEY"),
    "pinata_secret_api_key": os.getenv("PINATA_API_SECRET"),
}
# we get the api keys from create api keys section of pinata website


def main():
    with Path(filepath).open("rb") as fp:
        image_binary = fp.read()
        response = requests.post(
            PINATA_BASE_URL + endpoint,
            files={"file": (filename, image_binary)},
            headers=headers,
        )
        print(response.json())


if __name__ == "__main__":
    main()
