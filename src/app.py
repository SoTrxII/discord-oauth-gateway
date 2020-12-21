import os
from flask import Flask, g, session, redirect, request, url_for, jsonify
from requests_oauthlib import OAuth2Session
from base64 import b64encode, b64decode

OAUTH2_CLIENT_ID = os.environ['OAUTH2_CLIENT_ID']
OAUTH2_CLIENT_SECRET = os.environ['OAUTH2_CLIENT_SECRET']
OAUTH2_REDIRECT_URI = os.environ['OAUTH2_REDIRECT_URI']
#OAUTH2_REDIRECT_URI = 'http://localhost:5000/callback'

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET

if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'


def token_updater(token):
    session['oauth2_token'] = token


def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)


@app.route('/')
def index():
    scope = request.args.get(
        'scope',
        'identify email guilds')
    origin = request.args.get('callback') or request.headers.get("Host") or "localhost"
    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state + "_" + encodeB64(origin)
    return redirect(authorization_url)

def encodeB64(base):
    return b64encode(base.encode("ascii")).decode("ascii")

def decodeB64(base):
    return b64decode(base.encode("ascii")).decode("ascii")

@app.route('/callback')
def callback():
    if request.values.get('error'):
        return request.values['error']
    meh = session.get('oauth2_state')
    s,url = meh.split("_")
    print(f"Oauth callback with redirect : {decodeB64(url)}")
    discord = make_session(state=s)
    token = discord.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.url)

    session['oauth2_token'] = token
    return redirect(decodeB64(url))

@app.route('/me')
def me():
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me')
    if(user.status_code != 200):
        return (jsonify(user.json()), user.status_code)
    user = user.json()
    guilds = discord.get(API_BASE_URL + '/users/@me/guilds')
    if(guilds.status_code != 200):
        return (jsonify(guilds.json()), guilds.status_code)
    guilds = guilds.json()
    return jsonify(user=user, guilds=guilds)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
