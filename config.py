# Importamos os para leer las variables de configuración del sistema.
import os

# Importamos load_dotenv para cargar los datos guardados en el archivo .env.
from dotenv import load_dotenv


# Cargamos las variables del archivo .env para poder utilizarlas en Python.
load_dotenv()


# Creamos una clase para organizar la configuración de CliniApp.
class Config:

    # Clave secreta que Flask utiliza para proteger las sesiones.
    # Si no existe en el archivo .env, utiliza una clave para desarrollo local.
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-desarrollo-local")

    # Dirección del servidor donde está instalada la base de datos MySQL.
    # Si no se configura, utiliza localhost porque MySQL está en el mismo equipo.
    MYSQL_HOST = os.getenv("DB_HOST", "localhost")

    # Puerto que utiliza MySQL para recibir conexiones.
    # El valor predeterminado es 3306.
    MYSQL_PORT = int(os.getenv("DB_PORT", 3306))

    # Nombre del usuario utilizado para conectarse a MySQL.
    # Si no se configura, utiliza root.
    MYSQL_USER = os.getenv("DB_USER", "root")

    # Contraseña del usuario de MySQL.
    # Se obtiene del archivo .env para evitar escribirla directamente en el código.
    MYSQL_PASSWORD = os.getenv("DB_PASSWORD")

    # Nombre de la base de datos que utilizará la aplicación.
    # Si no se configura, utiliza cliniapp.
    MYSQL_DATABASE = os.getenv("DB_NAME", "cliniapp")

