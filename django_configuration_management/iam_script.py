import boto3
import json


def configure_iam():
    iam = boto3.client("iam")

    with open("config-iam.json") as file:
        json_data = json.load(file)
    namespace = json_data["namespace"]
    policies = json_data["policies"]
    iam_user_purpose = json_data["purpose"]
    user_exists = bool(json_data.get("arn"))

    policies_to_attach = list()
    policies_to_update = list()

    for policy in policies:
        description = policy.get("description")
        created = bool(policy.get("arn"))

        if not created:
            path_to_policy = policy["path"]
            purpose = policy["purpose"]

            with open(path_to_policy) as file:
                policy_json = file.read()
            response = iam.create_policy(
                PolicyName=f"{namespace}-{purpose}",
                PolicyDocument=policy_json,
                Description=description,
            )
            arn = response["Policy"]["Arn"]
            policy["arn"] = arn
            policies_to_attach.append(arn)
        else:
            policies_to_update.append(policy)

    username = f"{namespace}-{iam_user_purpose}"

    if not user_exists:
        response = iam.create_user(
            UserName=username,
        )
        arn = response["User"]["Arn"]
        json_data["arn"] = arn

    for policy_arn in policies_to_attach:
        iam.attach_user_policy(UserName=username, PolicyArn=policy_arn)
    for policy in policies_to_update:
        policy_arn = policy["arn"]
        results = iam.list_policy_versions(PolicyArn=policy_arn)
        versions = results["Versions"]
        for idx, version in enumerate(versions):
            version_id = version["VersionId"]
            if idx == 4:
                iam.delete_policy_version(PolicyArn=policy_arn, VersionId=version_id)

        with open(policy["path"]) as file:
            policy_json = file.read()
        response = iam.create_policy_version(
            PolicyArn=policy_arn, PolicyDocument=policy_json, SetAsDefault=True
        )

    with open("config-iam.json", "w") as file:
        json.dump(json_data, file, indent=2)