# Quick start

This package features an opinionated configuration management system, focused on combining both secret
and non-secret keys in the same configuration file. The values for secret keys are encrypted and can
be committed to the repo, but since each key is separated on a line-by-line basis, merge conflicts
shouldn't cause much trouble.

This package is intended to be used with a django project, though it's currently not making use
of any Django specific features.

Needless to say, this is in very early development.

## Install

`pip install django-configuration-management`

## cli

### Generate a key

In a terminal, enter:

```bash
generate_key
```

Follow the instructions printed to the console. For example, if you're setting up a production configuration,
make a file called `.env-production` in the root of your django project. Inside of it, save the key generated
above to a variable called `ENC_KEY`.

### Upsert a secret

To insert or update a secret, enter:

```bash
upsert_secret --environment <your environment>
```

And follow the prompts.

### Insert a non-secret

Simply open the .yml file for the generated stage (the naming scheme is `config-<environment>.yaml`),
and insert a row. It should look like this:

```yaml
USERNAME: whatsup1994 # non-secret
PASSWORD:
  secret: true
  value: gAAAAABf2_kxEgWXQzJ0SlRmDy6lbXe-d3dWD68W4aM26yiA0EO2_4pA5FhV96uMWCLwpt7N6Y32zXQq-gTJ3sREbh1GOvNh5Q==
```

### Insert an AWS Secret Manager secret

Add a row where the key name is your secret name in AWS Secret Manager, with a sub-key value pair of
`use_aws: true`. It should look like this:

```yaml
secrets/integrations/aws_secret:
  use_aws: true
  secret_keys:
    - AWS_SECRET
```

The secret in your AWS instance will need to conform to the naming patterns used elsewhere in
this repo, e.g., a properly structured AWS Secret Manager secret will look like

```json
{
  "AWS_SECRET": "I'm a secret"
}
```

The keys of this object will be translated into python variables for the Django settings
module in much the same way the keys of the local yaml will be, but you must explicitly
call out which keys you want to load by specifying the attribute `secret_keys`.

Your AWS credentials must also be set up correctly to make API calls to AWS.

### Manually editing the file

You can change the values of non-secrets by hand, as well as the keynames, but clearly you must
not change the value of secrets by hand, as they're encrypted. Changing the order of any of the
keys is perfectly fine.

### Print secrets to the console

To show the decrypted values of all the secrets in the console, enter:

```bash
reveal_secrets --environment <your-environment>
```

### Re-encrypt a config file

To re-encrypt all secret values for a given environment's config file, pass

```bash
reencrypt --environment <your-environment> --new-key <your-new-key>
```

If you do not provide a key, a new one will be generated for you.

## Configuring repository secrets from cli using `github_secrets`

To set secrets on a remote repository:

1. Create a `GITHUB_ACCESS_TOKEN` variable in your local shell environment.
   This variable should contain your github personal access token
   (https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token).
2. `cd` into the local repository that you would like to set secrets for.
3. Create a new file named `config-github.json` and add a JSON object where each
   key is the name of the secret you would like to add to the remote repository.
   The value can be an empty string or a brief description about the key.
   e.g.
   ```json
   {
     "AWS_ACCESS_KEY_ID": "Description",
     "AWS_SECRET_ACCESS_KEY": "Description"
   }
   ```
4. Run `github_secrets` to start running the script.
5. This will run the script and prompt you to enter a value for each secret key in
   the `config-github.json` file.
6. You can press `enter` to skip providing a value for any secret.
7. Once you have either provided a value or skipped all secrets in the `config-github.json` file,
   the script will push the secrets to the remote repository of the current working directory.

## Extras

In the root of your django project, you can create a file called `config-required.json`.

The JSON object can be a list or a dictionary. This is useful for validating the presence of your
keys on start-up.

Validating secrets that come from AWS Secret Manager is done implicitly since you must specify
a `secret_keys` attribute in your .yaml. This is needed so that only AWS secrets that are
explicitly called out are loaded into your Django settings/Python environment.

## Settings

There are two ways to use this library, if you don't mind a little magic, you can
simply inject the config by importing the following function in your django settings file,
and passing in the current module.

```python
# settings.py
from django_configuration_management import inject_config

# development is the environment name
inject_config("development", sys.modules[__name__])
```

See the example project for a demonstration of this.

If you want more verbosity, you can import the following function which will return
the config as a normalized dictionary that's flat and has all secrets decrypted.

```python
# settings.py
from django_configuration_management import get_config

# config = {"USERNAME": "helloworld", "PASSWORD": "im decrypted}
config = get_config("development")

USERNAME = config["USERNAME"]
# ...
```

### Using without a .env

If you want to skip using the .env, you can set the optional argument `dotenv_required` to `False`
when invoking either of the above two methods. Doing so means it then becomes your responsibility
to load an environment variable called `ENC_KEY` that stores the relevant encryption key for the
stage you're trying to load.

```python
# settings.py
from django_configuration_management import get_config

# Will error out if you didn't load ENC_KEY correctly
config = get_config("development", dotenv_required=False)
```

---

This project uses [poetry](https://python-poetry.org/) for dependency management
and packaging.
