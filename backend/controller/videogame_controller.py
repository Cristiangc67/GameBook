from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json
from peewee import fn
from model.database_model import Videojuego, Lista
from model.management_videogames import ManagementVideogames

class RequestHandler(BaseHTTPRequestHandler):
    @classmethod
    def extraer_datos(cls):
        return ManagementVideogames.data_extract()

    @classmethod
    def conectar_db(cls):
        return ManagementVideogames.conectar_db()

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def _set_error_headers(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        if parsed_path.path == '/search':
            self._handle_search(query)
        elif parsed_path.path == '/list':
            self._handle_list(query)
        else:
            self.send_error(404, 'Not Found')

    def _handle_search(self, query):
        filters = {}
        if 'nombre' in query:
            filters['nombre'] = query['nombre'][0]
        if 'genero' in query:
            filters['genero'] = query['genero'][0]

        results = (Videojuego
                   .select()
                   .where(fn.Lower(Videojuego.nombre).contains(filters.get('nombre', '').lower()),
                          fn.Lower(Videojuego.genero).contains(filters.get('genero', '').lower())))
        
        response = [{'id': v.id, 'nombre': v.nombre, 'genero': v.genero, 'plataforma': v.plataforma,
                     'desarrollador': v.desarrollador, 'publicador': v.publicador, 'fecha_lanzamiento': str(v.fecha_lanzamiento),
                     'ventas_totales': v.ventas_totales} for v in results]
        
        self._set_headers()
        self.wfile.write(json.dumps(response).encode())

    def _handle_list(self, query):
        if 'nombre' in query:
            try:
                lista = Lista.get(Lista.nombre == query['nombre'][0])
                response = {'nombre': lista.nombre, 'videojuegos': json.loads(lista.videojuegos)}
                self._set_headers()
                self.wfile.write(json.dumps(response).encode())
            except Lista.DoesNotExist:
                self.send_error(404, 'List not found')
        else:
            self.send_error(400, 'Bad Request')

    def do_POST(self):
        parsed_path = urlparse(self.path)
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        if parsed_path.path == '/list':
            self._handle_add_to_list(json.loads(post_data))
        else:
            self.send_error(404, 'Not Found')

    def _handle_add_to_list(self, data):
        print("Received data:", data)  # Agrega esta línea para depuración
        if 'nombre' in data and 'videojuego_ids' in data:
            lista, created = Lista.get_or_create(nombre=data['nombre'], defaults={'videojuegos': '[]'})
            videojuegos = json.loads(lista.videojuegos or '[]')

            # Verifica si los ids existen en la base de datos
            videojuegos_validos = (Videojuego
                                .select(Videojuego.id, Videojuego.nombre, Videojuego.plataforma, Videojuego.genero)
                                .where(Videojuego.id.in_(data['videojuego_ids'])))

            if not videojuegos_validos:
                self._set_error_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid videojuego_ids'}).encode())
                return

            # Agrega los videojuegos válidos a la lista
            for v in videojuegos_validos:
                videojuego_data = {
                    'id': v.id,
                    'nombre': v.nombre,
                    'plataforma': v.plataforma,
                    'genero': v.genero
                }
                videojuegos.append(videojuego_data)

            lista.videojuegos = json.dumps(videojuegos)
            lista.save()
            self._set_headers()
            self.wfile.write(json.dumps({'status': 'success'}).encode())
        else:
            self._set_error_headers(400)
            self.wfile.write(json.dumps({'error': 'Bad Request'}).encode())

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
