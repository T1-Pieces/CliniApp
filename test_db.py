
# Importamos la función de conexión desde el módulo db.
from app.db import get_connection


# Solicitamos una conexión con la base de datos.
conexion = get_connection()


# Comprobamos que la conexión se haya establecido correctamente.
if conexion and conexion.is_connected():

    # Mostramos un mensaje de confirmación.
    print("Conexion exitosa con la base de datos CliniApp")

    # Cerramos la conexión después de realizar la prueba.
    conexion.close()

    # Confirmamos que la conexión fue cerrada.
    print("Conexion cerrada correctamente")

else:
    # Informamos que no fue posible conectar con MySQL.
    print("No se pudo establecer la conexion con CliniApp")


