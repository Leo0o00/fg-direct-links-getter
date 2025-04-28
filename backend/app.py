from flask import Flask, request, jsonify
from flask_cors import CORS
from scraper import gather_direct_links
from cache import cache
from os import environ

from random import randint

app = Flask(__name__)
CORS(app)  # allow frontend localhost:3000
cache.init_app(app)


# Source: https://flask-caching.readthedocs.io/en/latest/
def make_key():
    """A function which is called to derive the key for a computed value.
      The key in this case is the concat value of all the json request
      parameters. Other strategy could to use any hashing function.
   :returns: unique string for which the value should be cached.
   """
    user_data = request.get_json()
    return ",".join([f"{key}={value}" for key, value in user_data.items()])


@app.route("/api/direct-links", methods=["POST"])
@cache.cached(timeout=86400, make_cache_key=make_key)
def api_direct_links():
    randnum = randint(1, 1000)
    print(randnum)
    data = request.get_json(force=True)
    url = data.get("url")
    for link in url:
        if not link or "https://fuckingfast.co/" not in link:
            return jsonify({"error": "Invalid FuckingFast URL"}), 400

    try:
        links = gather_direct_links(url)
        return jsonify({"links": links, "count": len(links)})
    except Exception as e:
        return jsonify({"error": "Unespected error while getting direct links"}), 500

# TODO: Estudiar como acceder a las variables de entorno
# TODO: Estudiar como habilitar el CORS para que solamente se pueda acceder desde el servidor de frontend
# TODO: Estudiar como implementar el rate-limit
# TODO: Estudiar como y donde desplegar el backend este
# TODO: Por ultimo y no menos importante REFACTORIZAR!!!


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
