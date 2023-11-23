# IU2FRL Lightsaber

This repo contains the python code of my lightsaber

## Original project

Original project comes from the [Lightsaber Prop-Maker RP2040](https://learn.adafruit.com/lightsaber-rp2040/overview) by [Ruiz brothers](https://learn.adafruit.com/u/pixil3d)

### Changes

The original project was too weak and had some design flaws, I decided to improve it and create my remix

## Hardware

1. [Adafruit RP2040 Prop-Maker Feather](https://www.adafruit.com/product/5768)
1. [Push button](https://www.adafruit.com/product/3350)
1. [Led strip](https://www.adafruit.com/product/2969)
1. [Mini speaker](https://www.adafruit.com/product/3923)
1. [Lithium battery](https://www.adafruit.com/product/1781)
1. [Mini switch](https://www.adafruit.com/product/805)
1. [3D printed parts]()
1. Some wires

## Auto deploy

### Configuration

1. Create virtualenv in root of project: `python -m venv venv`
1. Activate virtualenv: `source venv/bin/activate`
1. Install requirements: `pip install -r requirements.txt`

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