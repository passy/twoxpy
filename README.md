# Twoxpy

A tiny Twitter REST API proxy with an unpronouncable name.

## Setup

```
pip install -r requirements.txt
vim .env
dotenv python app.py
```

Or to run the production env:

`dotenv honcho start`

(Or `foreman` if you prefer that over `honcho`.)

### Example Environment

```
CONSUMER_KEY=my_key
CONSUMER_SECRET=my_secret
SECRET=cGLdIOw3ReC9WiZjHlOmiu7IbgmJoh9ab2yz+3HwTtMD6ebMqx3+20RsZD/HVum1Eg0=
DEBUG=True
```

## TODO

- Get this working with Python3. OAuthlib seems to have one incorrect conversion
  to bytes. Sigh...
- Properly set up CORS
- Find a proper redirection strategy.
