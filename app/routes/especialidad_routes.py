
# Importamos las herramientas necesarias de Flask.
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

# Importamos el tipo de error de MySQL.
from mysql.connector import Error

# Importamos la función para establecer conexiones con la base de datos.
from app.db import get_connection


# =========================================================
# CONFIGURACIÓN DEL MÓDULO
# =========================================================

# Blueprint que agrupa todas las rutas de especialidades.
especialidad_bp = Blueprint("especialidad", __name__)


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def obtener_especialidad(id_especialidad):
    """
    Consulta una especialidad mediante su identificador.

    Parámetros:
        id_especialidad: identificador de la especialidad.

    Retorna:
        Un diccionario con los datos de la especialidad
        o None si no existe.
    """

    # Establecemos la conexión con MySQL.
    conexion = get_connection()

    # Verificamos que la conexión se haya realizado.
    if conexion is None:
        raise ConnectionError("No se pudo conectar con MySQL.")

    # Inicializamos el cursor para garantizar su cierre.
    cursor = None

    try:
        # Creamos un cursor que devuelve los resultados como diccionarios.
        cursor = conexion.cursor(dictionary=True)

        # Consultamos la especialidad seleccionada.
        cursor.execute("""
            SELECT id_especialidad, nombre, descripcion
            FROM especialidad
            WHERE id_especialidad = %s
        """, (id_especialidad,))

        # Retornamos el registro encontrado.
        return cursor.fetchone()

    finally:
        # Cerramos el cursor si fue creado.
        if cursor is not None:
            cursor.close()

        # Cerramos la conexión con MySQL.
        conexion.close()


def obtener_datos_formulario():
    """
    Obtiene y valida los datos enviados desde un formulario HTML.

    Retorna:
        Una tupla con el nombre y la descripción.
        Retorna None cuando el nombre está vacío.
    """

    # Obtenemos los datos y eliminamos espacios innecesarios.
    nombre = request.form.get("nombre", "").strip()
    descripcion = request.form.get("descripcion", "").strip()

    # Validamos que el nombre sea obligatorio.
    if not nombre:
        return None

    # Retornamos los datos preparados para MySQL.
    return nombre, descripcion or None


def manejar_error_mysql(error):
    """
    Convierte errores frecuentes de MySQL en mensajes
    comprensibles para el usuario.

    Retorna:
        Una tupla con el mensaje y el código HTTP.
    """

    # Error 1062: nombre duplicado por una restricción UNIQUE.
    if error.errno == 1062:
        return "Ya existe una especialidad con ese nombre.", 409

    # Error 1451: existen registros relacionados con la especialidad.
    if error.errno == 1451:
        return (
            "No se puede eliminar la especialidad porque tiene médicos asociados.",
            409
        )

    # Registramos el error técnico para facilitar su diagnóstico.
    print("Error de MySQL:", error)

    # Mensaje general para los demás errores.
    return "Ocurrió un error al procesar la operación.", 500


# =========================================================
# 1. CONSULTAR ESPECIALIDADES (READ)
# =========================================================

@especialidad_bp.route("/especialidades", methods=["GET"])
def listar_especialidades():
    """
    Consulta todas las especialidades registradas.

    Método HTTP: GET
    Operación SQL: SELECT
    """

    # Establecemos la conexión con MySQL.
    conexion = get_connection()

    # Verificamos si fue posible conectar.
    if conexion is None:
        flash("No fue posible conectar con la base de datos.", "error")

        return render_template(
            "especialidades.html",
            especialidades=[]
        ), 500

    # Inicializamos el cursor.
    cursor = None

    try:
        # Creamos un cursor que devuelve los resultados como diccionarios.
        cursor = conexion.cursor(dictionary=True)

        # Consultamos las especialidades ordenadas alfabéticamente.
        cursor.execute("""
            SELECT id_especialidad, nombre, descripcion
            FROM especialidad
            ORDER BY nombre
        """)

        # Recuperamos todos los registros.
        especialidades = cursor.fetchall()

        # Mostramos el mensaje correspondiente a un registro exitoso.
        if request.args.get("registrado"):
            flash("Especialidad registrada correctamente.", "success")

        # Mostramos el mensaje correspondiente a una actualización exitosa.
        if request.args.get("actualizado"):
            flash("Especialidad actualizada correctamente.", "success")

        # Mostramos el mensaje correspondiente a una eliminación exitosa.
        if request.args.get("eliminado"):
            flash("Especialidad eliminada correctamente.", "success")

        # Enviamos los registros a la plantilla HTML.
        return render_template(
            "especialidades.html",
            especialidades=especialidades
        )

    except Error as error:
        # Registramos el error de consulta.
        print("Error al consultar especialidades:", error)

        flash("No fue posible consultar las especialidades.", "error")

        return render_template(
            "especialidades.html",
            especialidades=[]
        ), 500

    finally:
        # Cerramos el cursor si fue creado.
        if cursor is not None:
            cursor.close()

        # Cerramos la conexión.
        conexion.close()


# =========================================================
# 2. REGISTRAR ESPECIALIDAD (CREATE)
# =========================================================

@especialidad_bp.route(
    "/especialidades/nueva",
    methods=["GET", "POST"]
)
def registrar_especialidad():
    """
    Presenta el formulario y registra una especialidad.

    GET: muestra el formulario.
    POST: recibe los datos y ejecuta INSERT.
    """

    # Si la solicitud es GET, mostramos el formulario.
    if request.method == "GET":
        return render_template("formulario_especialidad.html")

    # Validamos los datos recibidos desde el formulario.
    datos = obtener_datos_formulario()

    # Comprobamos que el nombre no esté vacío.
    if datos is None:
        flash("El nombre de la especialidad es obligatorio.", "error")

        return render_template(
            "formulario_especialidad.html"
        ), 400

    # Establecemos la conexión con MySQL.
    conexion = get_connection()

    # Verificamos que la conexión esté disponible.
    if conexion is None:
        flash("Error de conexión con la base de datos.", "error")

        return render_template(
            "formulario_especialidad.html"
        ), 500

    # Inicializamos el cursor.
    cursor = None

    try:
        # Creamos el cursor para ejecutar la consulta.
        cursor = conexion.cursor()

        # Insertamos la nueva especialidad usando parámetros SQL.
        cursor.execute("""
            INSERT INTO especialidad (nombre, descripcion)
            VALUES (%s, %s)
        """, datos)

        # Confirmamos el registro en la base de datos.
        conexion.commit()

        # Redirigimos al listado con una señal de éxito.
        return redirect(
            url_for(
                "especialidad.listar_especialidades",
                registrado=1
            )
        )

    except Error as error:
        # Deshacemos la operación si ocurre un error.
        conexion.rollback()

        # Obtenemos el mensaje correspondiente al error.
        mensaje, codigo = manejar_error_mysql(error)

        flash(mensaje, "error")

        return render_template(
            "formulario_especialidad.html"
        ), codigo

    finally:
        # Cerramos el cursor si fue creado.
        if cursor is not None:
            cursor.close()

        # Cerramos la conexión.
        conexion.close()


# =========================================================
# 3. ACTUALIZAR ESPECIALIDAD (UPDATE)
# =========================================================

@especialidad_bp.route(
    "/especialidades/editar/<int:id_especialidad>",
    methods=["GET", "POST"]
)
def editar_especialidad(id_especialidad):
    """
    Consulta y actualiza la información de una especialidad.

    GET: muestra los datos actuales.
    POST: recibe los cambios y ejecuta UPDATE.
    """

    # -----------------------------------------------------
    # CONSULTAR LOS DATOS ACTUALES (GET)
    # -----------------------------------------------------

    if request.method == "GET":
        try:
            # Buscamos la especialidad mediante su identificador.
            especialidad = obtener_especialidad(id_especialidad)

            # Verificamos que el registro exista.
            if especialidad is None:
                flash("La especialidad no existe.", "error")

                return redirect(
                    url_for("especialidad.listar_especialidades")
                )

            # Mostramos el formulario con los datos encontrados.
            return render_template(
                "editar_especialidad.html",
                especialidad=especialidad
            )

        except (Error, ConnectionError) as error:
            # Registramos el error de consulta.
            print("Error al consultar especialidad:", error)

            flash(
                "No fue posible consultar la especialidad.",
                "error"
            )

            return redirect(
                url_for("especialidad.listar_especialidades")
            )

    # -----------------------------------------------------
    # VALIDAR LOS DATOS RECIBIDOS (POST)
    # -----------------------------------------------------

    # Obtenemos y validamos los datos del formulario.
    datos = obtener_datos_formulario()

    # Verificamos que el nombre sea obligatorio.
    if datos is None:
        flash(
            "El nombre de la especialidad es obligatorio.",
            "error"
        )

        return redirect(
            url_for(
                "especialidad.editar_especialidad",
                id_especialidad=id_especialidad
            )
        )

    # Establecemos la conexión con MySQL.
    conexion = get_connection()

    # Verificamos que la conexión esté disponible.
    if conexion is None:
        flash("Error de conexión con la base de datos.", "error")

        return redirect(
            url_for("especialidad.listar_especialidades")
        )

    # Inicializamos el cursor.
    cursor = None

    try:
        # Creamos el cursor para ejecutar las consultas.
        cursor = conexion.cursor()

        # Primero comprobamos que la especialidad exista.
        cursor.execute("""
            SELECT id_especialidad
            FROM especialidad
            WHERE id_especialidad = %s
        """, (id_especialidad,))

        # Recuperamos el identificador encontrado.
        especialidad_existente = cursor.fetchone()

        # Si no existe, cancelamos la operación.
        if especialidad_existente is None:
            conexion.rollback()

            flash(
                "No se encontró la especialidad para actualizar.",
                "error"
            )

            return redirect(
                url_for("especialidad.listar_especialidades")
            )

        # Actualizamos el nombre y la descripción.
        cursor.execute("""
            UPDATE especialidad
            SET nombre = %s,
                descripcion = %s
            WHERE id_especialidad = %s
        """, (*datos, id_especialidad))

        # Confirmamos los cambios en la base de datos.
        conexion.commit()

        # Redirigimos al listado con una señal de éxito.
        return redirect(
            url_for(
                "especialidad.listar_especialidades",
                actualizado=1
            )
        )

    except Error as error:
        # Deshacemos los cambios si ocurre un error.
        conexion.rollback()

        # Obtenemos el mensaje correspondiente al error.
        mensaje, codigo = manejar_error_mysql(error)

        flash(mensaje, "error")

        return redirect(
            url_for(
                "especialidad.editar_especialidad",
                id_especialidad=id_especialidad
            )
        )

    finally:
        # Cerramos el cursor si fue creado.
        if cursor is not None:
            cursor.close()

        # Cerramos la conexión.
        conexion.close()


# =========================================================
# 4. ELIMINAR ESPECIALIDAD (DELETE)
# =========================================================

@especialidad_bp.route(
    "/especialidades/eliminar/<int:id_especialidad>",
    methods=["POST"]
)
def eliminar_especialidad(id_especialidad):
    """
    Elimina una especialidad mediante su identificador.

    Método HTTP: POST
    Operación SQL: DELETE

    La base de datos impide eliminar especialidades
    que tengan médicos relacionados mediante una llave foránea.
    """

    # Establecemos la conexión con MySQL.
    conexion = get_connection()

    # Verificamos que la conexión esté disponible.
    if conexion is None:
        flash("Error de conexión con la base de datos.", "error")

        return redirect(
            url_for("especialidad.listar_especialidades")
        )

    # Inicializamos el cursor.
    cursor = None

    try:
        # Creamos el cursor para ejecutar la eliminación.
        cursor = conexion.cursor()

        # Ejecutamos DELETE con un parámetro seguro.
        cursor.execute("""
            DELETE FROM especialidad
            WHERE id_especialidad = %s
        """, (id_especialidad,))

        # Verificamos si se encontró un registro para eliminar.
        if cursor.rowcount == 0:
            # Cancelamos la operación si no hubo eliminación.
            conexion.rollback()

            flash("La especialidad no existe.", "error")

            return redirect(
                url_for("especialidad.listar_especialidades")
            )

        # Confirmamos la eliminación en MySQL.
        conexion.commit()

        # Redirigimos al listado con una señal de éxito.
        return redirect(
            url_for(
                "especialidad.listar_especialidades",
                eliminado=1
            )
        )

    except Error as error:
        # Deshacemos la operación si ocurre un error.
        conexion.rollback()

        # Obtenemos el mensaje correspondiente al error.
        mensaje, codigo = manejar_error_mysql(error)

        flash(mensaje, "error")

        return redirect(
            url_for("especialidad.listar_especialidades")
        )

    finally:
        # Cerramos el cursor si fue creado.
        if cursor is not None:
            cursor.close()

        # Cerramos la conexión.
        conexion.close()
