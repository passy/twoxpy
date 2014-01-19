# coding: utf-8

import os
import functools
from flask import Flask
from flask import g, session, request, url_for, flash, jsonify, abort
from flask import redirect, render_template
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
            return redirect(url_for('login', next=request.url))
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
@utils.crossdomain('*')
@require_login
def index():
    return jsonify({
        'user_id': g.user['user_id'],
        'screen_name': g.user['screen_name']
    })


@app.route('/1.1/<path:endpoint>', methods=['GET', 'POST'])
@utils.crossdomain('*')
@require_login
def proxy(endpoint):

    if request.method == 'GET':
        method = twitter.get
        data = request.args.to_dict()
    else:
        method = twitter.post
        data = request.form.to_dict()

    api_resp = method(endpoint, data=data)

    resp = jsonify(api_resp.data)
    resp.status_code = api_resp.status
    return resp


@app.route('/login')
def login():
    callback_url = url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@app.route('/logout')
def logout():
    session.pop('twitter_oauth', None)
    return redirect(url_for('index'))


@app.route('/oauthorized')
@twitter.authorized_handler
def oauthorized(resp):
    if resp is None:
        abort(403, 'You denied the request to sign in.')
    else:
        session['twitter_oauth'] = resp
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
