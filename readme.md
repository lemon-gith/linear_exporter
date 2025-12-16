# Linear Exporter

A pair of scripts used to extract [Linear](https://linear.app) issues out of a workspace, including their _full_ comment threads.

Inspired by code from [byelinear](https://github.com/terrastruct/byelinear), it just wasn't quite what I wanted. Lots of referencing Linear's [GraphQL docs](https://linear.app/developers/graphql).

Since my scripts tend to be functionally organised (somewhat), I thought it might be nice to upload this, in case anyone else stumbles upon the same problem I had (until Linear improves their own workspace export).

## Usage

```bash
# --------- Setup ---------

# create a virtual environment, because we are civilised
python -m venv venv

pip install -r requirements.txt

# my scripts need this environment variable for API authorisation
export LINEAR_API_KEY=<your Linear API key>

# --------- Execution ---------

# grab the issues, with all of their comments
python requester.py

# check filedump.json and make sure it has retrieved the data you want
# skim through the issues (LLL-dd.json), to verify the same thing

# optional: if you have media uploaded in your comment threads, pull them
python media_extracter.py

# verify that the images have all been retrieved
```

### Linear API Key

Can be found at `linear.app/<workspace name>/settings/account/security` `> Personal API keys`.

### `requester.py`

- Check this file first, to make sure it's getting the data you want
- May require some logic modification to make multiple requests (for larger workspaces)
  - i.e. repeated requests, using a variable to keep track of last comment/issue id

### `media_extracter.py`

- This only pulls files from `https://uploads.linear.app/...`
  - to have it pull any image (that it can access), edit [L106-L112](https://github.com/lemon-gith/linear_exporter/blob/0fbefbd6178346012c2054f5afab2d54d8a667f5/media_extracter.py#L106-L112)
- I only had it search:

  - `{ "description": ... }` and
  - `{ "comments": "nodes": "body": ... }`,

  if there are other places you've found images you'd like to pull, please feel free to add to `link_extracter()`

## Future

Really not much, I don't expect to further develop this script.
Forks are welcome and if I see a pull request, I may just merge it (no promises, though).
