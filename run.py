
# Importamos la función create_app desde el paquete app.
from app import create_app


# Creamos la instancia de nuestra aplicación Flask.
# Esta instrucción ejecuta la función create_app().
app = create_app()


# Verificamos que este archivo se esté ejecutando directamente.
# Esto evita iniciar el servidor si run.py se importa desde otro archivo.
if __name__ == "__main__":

    # Iniciamos el servidor de desarrollo de Flask.
    # debug=True permite detectar errores y recargar la aplicación
    # automáticamente cuando modificamos el código.
    app.run(debug=True)
