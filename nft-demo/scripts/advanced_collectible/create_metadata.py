# this will read offchain and create our metadata file

from brownie import AdvancedCollectible, network
from scripts.helpful_scripts import get_breed
from metadata.sample_metadata import metadata_template
from pathlib import Path
import requests
import json
import os

breed_to_image_uri = {
    "PUG": "https://ipfs.io/ipfs/QmSsYRx3LpDAb1GZQm7zZ1AuHZjfbPkD6J7s9r41xu1mf8?filename=pug.png",
    "SHIBA_INU": "https://ipfs.io/ipfs/QmYx6GsYAKnNzZ9A6NvEKV9nf1VaDzJrqDR23Y8YSkebLU?filename=shiba-inu.png",
    "ST_BERNARD": "https://ipfs.io/ipfs/QmUPjADFGEKmfohdTaNcWhp7VGk26h5jXDA7v3VtTnTLcW?filename=st-bernard.png",
}


def main():
    advanced_collectible = AdvancedCollectible[-1]
    # getting most recently deployed contract
    # getting number of tokens
    number_of_advanced_collectibles = advanced_collectible.tokenCounter()
    print(f"You have created {number_of_advanced_collectibles} collectibles!")
    # after getting contract and number of tokens, we can loop through all of the tokens and get metadata
    for token_id in range(number_of_advanced_collectibles):
        breed = get_breed(advanced_collectible.tokenIdToBreed(token_id))
        # tokenid is integer and inside the paranthesis will return a string equals to breed
        # below checking first to see if we have the metadata file already
        metadata_file_name = f"./metadata/{network.show_active()}/{token_id}-{breed}.json"  # creating a json file of metadata
        # below we check if metadata file already exists
        collectible_metadata = metadata_template
        if Path(metadata_file_name).exists():
            # above Path is library to find path of the file metadata_file_name
            print(f"{metadata_file_name} already exists! Delete it to overwrite")
        else:
            print(f"Creating Metadata file: {metadata_file_name}")
            collectible_metadata["name"] = breed
            collectible_metadata["description"] = f"An adorable {breed} pup!"
            image_path = "./img/" + breed.lower().replace("_", "-") + ".png"
            # above creating image path for our image
            # .lower() makes lowercase

            image_uri = None
            if os.getenv("UPLOAD_IPFS") == "true":
                image_uri = upload_to_ipfs(image_path)
            image_uri = image_uri if image_uri else breed_to_image_uri[breed]
            # above says image_uri equals to image_uri if image_uri isnt none else it is from mapping breed to image uri

            collectible_metadata["image"] = image_uri
            # above is setting image_uri to image on collectible_metadata dictionary/mapping
            # now image is uploaded to ipfs, next we need to upload metadata to ipfs

            with open(metadata_file_name, "w") as file:
                # above writing metadata_file_name to file variable
                json.dump(collectible_metadata, file)
                # above this will dump file to collectible_metadata as json file
            if os.getenv("UPLOAD_IPFS") == "true":
                upload_to_ipfs(metadata_file_name)


# curl -X POST -F file=@metadata/rinkeby/0-SHIBA_INU.json http://localhost:5001/api/v0/add

# below is a function to upload token image to ipfs and return imageURI
def upload_to_ipfs(
    filepath,
):
    # filepath is the location where our token image resides, which we are gonna upload to ipfs
    with Path(filepath).open("rb") as fp:
        # above, rb means opening filepath as binary since images can be opened as binary and saving in fp variable
        image_binary = fp.read()  # now whole image binary is stored in image_binary

        # we actually want to upload our images to our own ipfs node
        # then we can run our own node by typing in command line "ipfs daemon"
        # ipfs url will be the WebUI written in command line
        # then we have to apicall or post request to ipfs url using the endpoint
        # after running own ipfs node, we should keep it running and open new terminal by plus button

        # IMPORTANT: as we cant keep running our own node always, and it goes down, nobody can see our images,
        # it is better to upload everything to 3rd party service as well as our own node
        # here deploy_to_pinata comes into play

        ipfs_url = "http://127.0.0.1:5001"
        endpoint = "/api/v0/add"  # this is the endpoint and used to make api call to above ipfs url, taken from https://docs.ipfs.io/reference/http/api/#api-v0-add
        # having ipfs url and endpoint, we can make a post request/api call
        response = requests.post(  # requests is a python package
            ipfs_url + endpoint, files={"file": image_binary}
        )  # says files we are gonna upload equals to image_binary

        # if we look at the sample uri below, ipfs stores everything in a hash, which represents the json file at the end
        # sample_token_uri = "https://ipfs.io/ipfs/Qmd9MCGtdVz2miNumBHDbvj8bigSgTwnr4SbyH6DNnpWdt?filename=0-PUG.json"
        # ipfs response returns bytes, hash, name and size, we care about the hash since everything is stored in there
        ipfs_hash = response.json()["Hash"]
        # above will grab the hash key from response dictionary
        filename = filepath.split("/")[-1:][0]
        # above says filename equals to last part of the filepath variable by splitting up by /, "./img/0-PUG.png" -> "0-PUG.png"
        image_uri = f"https://ipfs.io/ipfs/{ipfs_hash}?filename={filename}"  # after hash and filename, it will appear as below
        # sample_token_uri = "https://ipfs.io/ipfs/Qmd9MCGtdVz2miNumBHDbvj8bigSgTwnr4SbyH6DNnpWdt?filename=0-PUG.json"
        print(image_uri)
        return image_uri
