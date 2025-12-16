import json
import os
import requests


# define query up here, to avoid bloating fn definition.
# feel free to modify the `last: ???` value, I just picked 100
# because it seemed like enough for my workspace
request ="""
query($before: String, $number: Float) {
    issues(last: 100, before: $before, filter: {number: {eq: $number}}, includeArchived: true) {
        nodes {
            id
            url
            identifier
            title
            description
            creator {
                name
                email
            }
            assignee {
                name
                email
            }
            priorityLabel
            state {
                name
            }
            project {
                name
                description
            }
            createdAt
            labels(last: 20) {
                nodes {
                    name
                    color
                    description
                }
            }
            comments(last: 10) {
                nodes {
                    url
                    user {
                        name
                        email
                    }
                    createdAt
                    body
                }
            }
            attachments(last: 10) {
                nodes {
                    url
                }
            }
            relations(last: 10) {
                nodes {
                    relatedIssue {
                        identifier
                    }
                }
            }
            parent {
                identifier
            }
            children(last: 10) {
                nodes {
                    identifier
                }
            }
        }
    }
}
"""
# query string modified from https://github.com/terrastruct/byelinear/blob/03a203aa310fa46721cd102c24ed75fdcdcccf41/linear.go#L27-L92


def get_data(outputfile: str, url: str = "https://api.linear.app/graphql"):
    if os.path.isfile(outputfile):
        print(f"{outputfile} already exists, using cached file")
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": os.environ.get("LINEAR_API_KEY")
    }

    response = requests.post(url=url, headers=headers, json={"query": request})

    if response.status_code == 200:
        js_file = json.loads(response.content.decode('utf-8'))
        with open(os.path.join(os.getcwd(), "filedump.json"), "w+") as f:
            json.dump(js_file, f, indent=4)
    else:
        raise Exception(
            "Encountered error making GraphQL request:\n",
            f"Status Code: {response.status_code},\n"
            f"API Key: {os.environ.get("LINEAR_API_KEY")}\n"
        )


def split_data(datafile: str, target_dir: str):
    with open(os.path.join(os.getcwd(), datafile), "r+") as f:
        data = json.load(f)
        for node in data["data"]["issues"]["nodes"]:
            name = node["identifier"]
            os.makedirs(target_dir, exist_ok=True)
            with open(
                os.path.join(os.getcwd(), f"{target_dir}/{name}.json"), "w+"
            ) as out:
                json.dump(node, out, indent=4)


if __name__ == "__main__":
    # save as file, to avoid making repeated requests, on processing
    intermediate_file = "filedump.json"

    get_data(intermediate_file)

    split_data(intermediate_file, "issues")
