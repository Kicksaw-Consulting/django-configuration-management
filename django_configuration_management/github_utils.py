import requests
import json
import subprocess
import re
from base64 import b64encode
from nacl import encoding, public
from nacl.public import SealedBox
import nacl.utils


def get_remote_repo():
    result = subprocess.Popen("git remote -v", shell=True, stdout=subprocess.PIPE)

    if result is None:
        print("Local repository could not be determined. Exiting...")
        quit()

    repo_result_w_byte = result.stdout.read()
    stripped = repo_result_w_byte.decode(
        "utf-8-sig"
    ).rstrip()  # Remove byte order mark and new line

    return stripped


def owner_and_repo():
    repo_url = get_remote_repo()
    owner_and_repo = re.search("[A-Za-z0-9]+\/[A-Za-z0-9_-]+\.git", repo_url).group()
    owner_repo_array = owner_and_repo.split("/")
    owner = owner_repo_array[0]
    repo_name = owner_repo_array[1].split(".")[0]

    if owner is None:
        print(f"Owner for repository could not be found. Exiting...")
        quit()

    if repo_name is None:
        print(f"Repository name could not be determined. Exiting...")
        quit()
    return [owner, repo_name]


def repository_info(github_access_token, owner, repo_name):
    # Get a repository public key
    headers = {"Authorization": "token " + github_access_token}
    repo_public_key_string = requests.get(
        f"https://api.github.com/repos/{owner}/{repo_name}/actions/secrets/public-key",
        headers=headers,
    ).text
    repo_public_key_dict = json.loads(repo_public_key_string)
    repo_key = repo_public_key_dict["key"]
    key_id = repo_public_key_dict["key_id"]
    return [repo_key, key_id]


def encrypt_secret(user_public_key: str, secret_value: str):
    """
    Encrypt a Unicode string using the public key.
        https://docs.github.com/en/rest/reference/actions#create-or-update-a-repository-secret
    """
    public_key = public.PublicKey(
        user_public_key.encode("utf-8"), encoding.Base64Encoder()
    )
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")


def push_secrets_to_github(
    owner, repo_name, key_id, secrets_dictionary, github_access_token
):
    for secret_key in secrets_dictionary:
        headers = {
            "accept": "application/vnd.github.v3+json",
            "Authorization": "token " + github_access_token,
        }
        payload = {
            "owner": owner,
            "repo": repo_name,
            "secret_name": secret_key,
            "encrypted_value": secrets_dictionary[secret_key],
            "key_id": key_id,
        }
        url = f"https://api.github.com/repos/{owner}/{repo_name}/actions/secrets/{secret_key}"
        print(f"Pushing secrets to url: {url}")
        try:
            response = requests.put(url, headers=headers, data=json.dumps(payload))
        except Exception as e:
            print(f"Failed to push secrets to remote repository: {e}")
