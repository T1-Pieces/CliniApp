
# Importamos Flask para crear la aplicación web.
from flask import Flask, render_template

# Importamos la configuración general del proyecto.
from config import Config

# Importamos el Blueprint del módulo de pacientes.
from app.routes.paciente_routes import paciente_bp

# Importamos el Blueprint del módulo de especialidades.
from app.routes.especialidad_routes import especialidad_bp


def create_app():
    """
    Crea y configura la aplicación principal de CliniApp.

    Carga la configuración, registra los módulos de pacientes
    y especialidades, y define la ruta de inicio.
    """

    # Inicializamos la aplicación Flask.
    app = Flask(__name__)

    # Cargamos la configuración general del proyecto.
    # Esto permite utilizar SECRET_KEY y las demás variables
    # definidas en la clase Config.
    app.config.from_object(Config)

    # Registramos las rutas del módulo de pacientes.
    app.register_blueprint(paciente_bp)

    # Registramos las rutas del módulo de especialidades.
    app.register_blueprint(especialidad_bp)

    # Definimos la ruta principal de la aplicación.
    @app.route("/")
    def inicio():
        """
        Muestra la página principal de CliniApp.
        """
        return render_template("index.html")

    # Devolvemos la aplicación Flask configurada.
    return app
