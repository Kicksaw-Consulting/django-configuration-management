from django_configuration_management.yml_utils import yml_to_dict


def test_yml_to_dict():
    data = yml_to_dict("test")
    assert data == {
        "PASSWORD": {
            "secret": True,
            "value": "gAAAAABgPsL6dJtRSNdwf2lIV4xVZaBZl1ZTTA6TEriYouHt-IMh1fIxf18GPsqzxfaSyFNXiMMJ5xL2DwlQc8QdwPTOlhJGKQ==",
        },
        "USERNAME": "testusername",
        "secrets/integrations/aws_secret": {"use_aws": True},
    }
