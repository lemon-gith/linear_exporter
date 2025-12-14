import re
import json
import os
import glob
import requests
import io
import PIL.Image as Image


def extract_links(content: str):
    """only extracts media links based on markdown `![$name]($link)` format"""
    files = list()

    if (
        lnk_matches := re.findall(r"\!\[.+\]\(.*\)", content
    )) == []:
        return []

    for embed_txt in lnk_matches:
        [media_filename, rest] = (
            embed_txt.split('[')[1]
        ).split(']')

        media_link = rest[1:-1]

        files.append((media_filename, media_link))

    return files


def link_extracter(data_dir: str = "issues"):
    """Assumes data is split by `requester.py`. Also assumes Linear JSON structure from 14/12/2025:
    ```
    {
        "data": {
            "issues": {
                "nodes": [
                    {
                        ...
                        "description": str,
                        ...
                        "comments": {
                            "nodes": [
                                {
                                    ...
                                    "body": str,
                                },
                            ],
                        },
                        ...
                    },
                    ...
                ]},
            },
        },
    }
    ```"""
    files = list()

    for filename in glob.glob(f"{data_dir}/ACC-*.json"):
        with open(os.path.join(os.getcwd(), filename), 'r') as f:
            file = json.load(f)

            if not file["description"]:
                print(f"{filename} doesn't have a 'description'")
            else:
                if len((media := extract_links(file["description"]))) > 0:
                    print(f"In {filename}/description: found matches {media}")
                    files.extend(media)


            if not file["comments"]:
                print(f"Wait, {filename} doesn't even have 'comments'?")
                continue

            if not file["comments"]["nodes"]:
                print(f"aww, no comments in file {filename}")
                continue

            for comment in file["comments"]["nodes"]:
                content: str = comment["body"]

                if len((media := extract_links(content))) > 0:
                    print(f"In {filename}/comments: found matches {media}")
                    files.extend(media)


    with open(os.path.join(os.getcwd(), "media_files.txt"), "w+") as output:
        for (name, link) in files:
            output.write(f"\"{name}\",{link},\n")

    return files


def get_media(name_link_pairs, target_dir: str = "images"):
    """retrieves the extracted media files from Linear's servers"""
    # saving to an `images/`, as that makes sense
    # if you want to save somewhere else, change `image.save(...)` below, too
    os.makedirs(target_dir, exist_ok=True)

    headers = {
        "Authorization": os.environ.get("LINEAR_API_KEY")
    }

    for (name, url) in name_link_pairs:
        if url.find("uploads.linear.app") < 0:
            print(
                f"File: '{name}', at url: {url}\n",
                "does not appear to be a Linear-stored file",
                "please retrieve it manually, or modify this script"
            )
            continue  # is not a linear file to be pulled

        response = requests.get(url=url, headers=headers)

        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            image.save(os.path.join(os.getcwd(), f"{target_dir}/{name}"))
        else:
            print(
                "Encountered error making GraphQL request:\n",
                f"Status Code: {response.status_code},\n"
                f"API Key: {os.environ.get("LINEAR_API_KEY")}\n"
            )


if __name__ == "__main__":
    link_name_pairs = link_extracter("issues")

    get_media(link_name_pairs, "images")
