"""
server

Framework for server that runs backend for NBAdle
"""

from json import dumps
from flask import Flask, request
from flask_cors import CORS
from player import get_player, get_names, get_player_by_full_name


def default_handler(err):
    """
    Flask route for default handler function
    """
    response = err.get_response()
    print("response", err, err.get_response())
    response.data = dumps(
        {
            "code": err.code,
            "name": "System Error",
            "message": err.get_description(),
        }
    )
    response.content_type = "application/json"
    return response


app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def get_home():
    """
    Flask route for home
    """
    return "Hello"


@app.route("/api/getplayer", methods=["GET"])
def get_random_player():
    """
    Flask route to get player on home page
    """
    return dumps(get_player())


@app.route("/api/getnames", methods=["GET"])
def get_player_names():
    """
    Flask route to get player names
    """
    return dumps(get_names())


@app.route("/api/getguessedplayer", methods=["GET"])
def get_guessed_player():
    """
    Flask route to get player stats from guessed name
    """
    full_name = request.args.get("guess")
    return dumps(get_player_by_full_name(full_name))


if __name__ == "__main__":
    app.run(debug=True)
