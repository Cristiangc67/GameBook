from flask import (
    Flask,
    render_template,
    request,
    send_from_directory,
    redirect,
    url_for,
)
import requests

app = Flask(__name__, static_folder="static")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/home", methods=["GET", "POST"])
def home():
    generes = [
        "Action",
        "Adventure",
        "Fighting",
        "Misc",
        "Platform",
        "Puzzle",
        "Racing",
        "Role-Playing",
        "Shooter",
        "Simulation",
        "Sports",
        "Strategy",
    ]
    results = []
    if request.method == "GET":
        nombre = request.args.get("nombre", "")

        genero = request.args.get("genero", "")

        if nombre or genero:

            params = {"nombre": nombre, "genero": genero}

            response = requests.get("http://localhost:8000/search", params=params)
            if response.status_code == 200:
                results = response.json()
    elif request.method == "POST":
        gameId = request.form["juego_id"]
        lista = request.form["lista_favoritos"]
        data = {"nombre": lista, "videojuego_ids": [gameId]}
        response = requests.post("http://localhost:8000/list", json=data)
        if response.status_code == 200:
            return redirect(url_for("mislistas"))
        else:
            return redirect(url_for("mislistas"))

    return render_template("home.html", generes=generes, results=results)


@app.route("/mislistas", methods=("GET", "POST"))
def mislistas():
    if request.method == "POST":
        name = request.form["nombre"]

        data = {"nombre": name, "videojuego_ids": []}

        response = requests.post("http://localhost:8000/list", json=data)
        if response.status_code == 200:
            return redirect(url_for("mislistas"))
        else:
            return redirect(url_for("mislistas"))
        # return f"Error: {response.text}", response.status_code

    return render_template("mislistas.html")


@app.route("/mislistas/favoritos")
def listid():
    params = {"nombre": "favoritos"}
    response = requests.get("http://localhost:8000/list", params=params)

    if response.status_code == 200:
        results = response.json()
        print("aca esta el result")
        print("Results:", results)
        return render_template("listaId.html", results=results)
    else:
        print("Error:", response.text)
        return "Error al obtener la lista de favoritos", 500


@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory("frontend/static", path)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
