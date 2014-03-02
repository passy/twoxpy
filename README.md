# Twoxpy

A tiny Twitter REST API proxy with an unpronouncable name for Python 2 and
Python 3.

## Setup

```
pip install -r requirements.txt
vim .env
dotenv python app.py
```

Or to run the production env:

`honcho start`

(Or `foreman` if you prefer that over `honcho`.)

### Example Environment

```
CONSUMER_KEY=my_key
CONSUMER_SECRET=my_secret
SECRET=cGLdIOw3ReC9WiZjHlOmiu7IbgmJoh9ab2yz+3HwTtMD6ebMqx3+20RsZD/HVum1Eg0=
DEBUG=True
DEFAULT_ORIGIN=http://localhost:9000
ACCOUNT_WHITELIST=horse_js,passy,sindresorhus
```

## API

- `GET /login`: Redirects to the user login
- `POST /logout`
- `GET|POST /1.1/<path:endpoint>`: Proxies the signed request

For more, just read the source, Luke. It's really not that much.

## TODO

- Get this working with Python3. OAuthlib seems to have one incorrect conversion
  to bytes. Sigh...
