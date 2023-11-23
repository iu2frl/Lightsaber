# Lightsaber

Python code of my Lightsaber

## Auto deploy

### Configuration

1. Create virtualenv in root of project: `python -m venv venv`
2. Activate virtualenv: `source venv/bin/activate`
3. Install requirements: `pip install -r requirements.txt`

### Deploy

After the environment has been set you can deploy to the board using the `RUN and debug` button

- `Full deploy`: will copy all files and libraries (slow)
- `Python only`: will copy only *.py files (faster)

### Note

Tested on:

```txt
PRETTY_NAME="Ubuntu 22.04.3 LTS"
NAME="Ubuntu"
VERSION_ID="22.04"
VERSION="22.04.3 LTS (Jammy Jellyfish)"
VERSION_CODENAME=jammy
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=jammy
```