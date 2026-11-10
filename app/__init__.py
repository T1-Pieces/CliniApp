
# Importamos Flask para crear la aplicación web.
from flask import Flask

# Importamos el Blueprint del módulo de pacientes.
from app.routes.paciente_routes import paciente_bp


# Creamos la función principal de la aplicación.
def create_app():

    # Inicializamos Flask.
    app = Flask(__name__)

    # Registramos las rutas del módulo de pacientes.
    app.register_blueprint(paciente_bp)

    # Definimos la ruta principal.
    @app.route("/")
    def inicio():

        # Mostramos la página de bienvenida.
        from flask import render_template
        return render_template("index.html")

    # Devolvemos la aplicación configurada.
    return app
