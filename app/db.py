
# Importamos mysql.connector para conectar Python con MySQL.
import mysql.connector

# Importamos Error para controlar posibles errores de conexión.
from mysql.connector import Error

# Importamos Config para obtener los datos del archivo .env.
from config import Config


# Definimos una función reutilizable para conectarnos a MySQL.
def get_connection():

    try:
        # Establecemos la conexión utilizando los datos de configuración.
        conexion = mysql.connector.connect(

            # Dirección del servidor MySQL.
            host=Config.MYSQL_HOST,

            # Puerto de conexión de MySQL.
            port=Config.MYSQL_PORT,

            # Usuario de acceso a la base de datos.
            user=Config.MYSQL_USER,

            # Contraseña del usuario de MySQL.
            password=Config.MYSQL_PASSWORD,

            # Nombre de la base de datos de CliniApp.
            database=Config.MYSQL_DATABASE
        )

        # Devolvemos la conexión para que otros módulos puedan utilizarla.
        return conexion

    except Error as error:
        # Mostramos el error si no fue posible establecer la conexión.
        print("Error al conectar con MySQL:", error)

        # Devolvemos None para indicar que la conexión no se pudo realizar.
        return None
