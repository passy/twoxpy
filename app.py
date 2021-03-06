# coding: utf-8

import os
import functools
from flask import Flask
from flask import g, session, request, url_for, jsonify, redirect
from flask_oauthlib.client import OAuth

import utils


app = Flask(__name__)
app.debug = os.environ.get('DEBUG') == 'True'
app.secret_key = os.environ.get('SECRET')

oauth = OAuth(app)

twitter = oauth.remote_app(
    'twitter',
    consumer_key=os.environ.get('CONSUMER_KEY'),
    consumer_secret=os.environ.get('CONSUMER_SECRET'),
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
)


def enforce_referer(fn):

    @functools.wraps(fn)
    def _inner(*args, **kwargs):
        referrer = request.headers.get('Referer')

        if referrer is None or \
            not referrer.startswith(os.environ.get('DEFAULT_ORIGIN')):

            return json_abort(403, 'Missing or invalid Referrer.')

        return fn(*args, **kwargs)

    return _inner


def json_abort(code, msg):
    response = jsonify({
        'message': msg
    })
    response.status_code = code

    return response


def require_login(fn):

    @functools.wraps(fn)
    def _inner(*args, **kwargs):
        if g.user is None:
            return json_abort(403, 'Login required. Go to /login.')
        return fn(*args, **kwargs)

    return _inner


@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']


@app.before_request
def before_request():
    g.user = None
    if 'twitter_oauth' in session:
        g.user = session['twitter_oauth']


@app.route('/')
@enforce_referer
@utils.crossdomain()
@require_login
def index():
    return jsonify({
        'user_id': g.user['user_id'],
        'screen_name': g.user['screen_name']
    })


# Sending a Content-Type will require an additional OPTIONS pre-flight
# request.
@app.route('/1.1/<path:endpoint>', methods=['GET', 'POST', 'OPTIONS'])
@enforce_referer
@utils.crossdomain(headers=['content-type'])
@require_login
def proxy(endpoint):
    content_type = request.headers.get('content-type')

    if request.method == 'GET':
        method = twitter.get
        data = request.args.to_dict()
    else:
        method = twitter.post
        if content_type == 'application/json':
            data = request.stream.read()
        else:
            # Otherwise keep the default
            content_type = None
            data = request.form.to_dict()

    api_resp = method(endpoint,
                      content_type=content_type,
                      data=data)

    if type(api_resp.data) is list:
        # This will never happen, right? Because people know that this is bad.
        # RIGHT?
        api_resp.data = { 'data': api_resp.data }

    resp = jsonify(api_resp.data)
    resp.status_code = api_resp.status
    return resp


@app.route('/login')
def login():
    callback_url = url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@app.route('/logout', methods=['POST'])
@enforce_referer
@utils.crossdomain()
def logout():
    session.pop('twitter_oauth', None)
    return jsonify({'message': 'Logout successful'})


@app.route('/oauthorized')
@twitter.authorized_handler
def oauthorized(resp):
    if resp is None:
        return json_abort(403, 'You denied the request to sign in.')
    elif not verify_account(resp):
        return json_abort(403, 'Your account has not been whitelisted yet.')
    else:
        session['twitter_oauth'] = resp

    # Not quite sure about the security implications of this ...
    if request.args['next']:
        return redirect(request.args['next'])
    else:
        return jsonify({'message': 'You are successfully authorized'})


def verify_account(resp):
    """If an account whitelist is set, check that the given screen name is
    part of it.
    """
    whitelist = os.environ.get('ACCOUNT_WHITELIST')
    if whitelist is None:
        return True

    return resp['screen_name'].lower() in [w.lower() for w in
                                           whitelist.split(',')]


if __name__ == '__main__':
    app.run()
