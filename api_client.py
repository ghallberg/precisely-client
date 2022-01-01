import requests
import json
import os
from dotenv import load_dotenv
from io import open

#TODO: Move config-handling to module/class if needed
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
USER_NAME = os.getenv("USER_NAME")
PASSWORD = os.getenv("PASSWORD")
OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER")

# TODO: Rate-limit handling (waiting until X-Ratelimit-Reset when X-Ratelimit-Remaining is 0)
#       Not needed with a single org, with few docs.
# TODO: Verify responses with openapi?
# TODO: Move functions into module/class for readability


def get_auth_header():
    auth_resp = requests.post(
        f"{BASE_URL}/authenticate",
        json={
            "userName": USER_NAME,
            "password": PASSWORD,
        },
    )

    return {"Authorization": f"Bearer {auth_resp.json()['accessToken']}"}


def get_orgs(auth_header):
    org_resp = requests.get(
        f"{BASE_URL}/organizations",
        headers=auth_header,
    )

    return org_resp.json()


def write_org_docs(org_id, auth_header):
    docs_resp = requests.get(
        f"{BASE_URL}/organizations/{org_id}/documents",
        headers=auth_header,
    )

    for doc in docs_resp.json():
        doc_id = doc["id"]
        doc_dir = f"{OUTPUT_FOLDER}/org_{org_id}/{doc_id}"

        if not os.path.exists(doc_dir):
            os.makedirs(doc_dir)

        pdf_resp = requests.get(
            f"{BASE_URL}/organizations/{org_id}/documents/{doc_id}/pdf",
            headers=auth_header,
        )

        # TODO: Currently overwriting everything without asking.
        with open(f"{doc_dir}/{doc_id}.pdf", "wb") as pdf_file:
            print(f"Creating PDF for doc: {doc_id}")
            pdf_file.write(pdf_resp.content)

        with open(f"{doc_dir}/{doc_id}.json", "w") as json_file:
            print(f"Creating JSON for doc: {doc_id}")
            json.dump(doc, json_file)


if __name__ == "__main__":
    auth_header = get_auth_header()
    orgs = get_orgs(auth_header)

    for org in orgs:
        org_id = org["id"]
        write_org_docs(org_id, auth_header)
