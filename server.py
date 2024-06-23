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
    availableLists = requests.get("http://localhost:8000/lists")
    if availableLists.status_code == 200:
        availableLists = availableLists.json()
    else:
        availableLists = []
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
        lista = request.form["lista_name"]
        data = {"nombre": lista, "videojuego_ids": [gameId]}
        response = requests.post("http://localhost:8000/list", json=data)
        if response.status_code == 200:
            return redirect(
                url_for(
                    "home",
                    nombre=request.args.get("nombre"),
                    genero=request.args.get("genero"),
                )
            )
        else:
            return redirect(url_for("home"))

    return render_template(
        "home.html", generes=generes, results=results, availableLists=availableLists
    )


@app.route("/mislistas", methods=("GET", "POST"))
def mislistas():

    if request.method == "POST":
        name = request.form.get("nombre")
        delete_name = request.form.get("delete_nombre")
        if delete_name:

            data = {"nombre": delete_name}
            response = requests.post("http://localhost:8000/delete_list", json=data)
            if response.status_code == 200:
                return redirect(url_for("mislistas"))
            else:
                return redirect(url_for("mislistas"))
        else:
            data = {"nombre": name, "videojuego_ids": []}
            response = requests.post("http://localhost:8000/list", json=data)
            if response.status_code == 200:
                return redirect(url_for("mislistas"))
            else:
                return redirect(url_for("mislistas"))
        # return f"Error: {response.text}", response.status_code

    elif request.method == "GET":
        response = requests.get("http://localhost:8000/lists")
        if response.status_code == 200:
            listas = response.json()
            return render_template("mislistas.html", listas=listas)
        else:
            return render_template("mislistas.html", error="Error fetching data")

    return render_template("mislistas.html")


@app.route("/mislistas/<string:name>", methods=["GET", "POST"])
def listid(name):
    params = {"nombre": name}
    response = requests.get("http://localhost:8000/list", params=params)

    if response.status_code == 200:
        results = response.json()

        if request.method == "POST":
            gameId = request.form.get("juego_id")
            listName = request.form.get("lista_name")
            gameId = int(gameId)
            data = {"nombre": listName, "videojuego_id": gameId}
            eraseResponse = requests.post(
                "http://localhost:8000/remove_game", json=data
            )

            if eraseResponse.status_code == 200:

                return redirect(url_for("listid", name=name))
            else:
                print("Error al eliminar el juego:", eraseResponse.text)
                return "Error al eliminar el juego", 500

        return render_template("listaId.html", results=results)
    else:
        print("Error al obtener la lista de juegos:", response.text)
        return "Error al obtener la lista de juegos", 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
