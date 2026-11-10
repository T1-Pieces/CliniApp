
# Importar las herramientas necesarias de Flask.
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)

# Importar la conexión con MySQL.
from app.db import get_connection
from mysql.connector import Error


# Crear el Blueprint del módulo de pacientes.
paciente_bp = Blueprint("pacientes", __name__)


# =====================================================
# LISTAR PACIENTES
# =====================================================
@paciente_bp.route("/pacientes")
def listar_pacientes():

    pacientes = []
    mensaje_error = None
    mensaje_exito = None

    # Identificar si existe un mensaje de éxito.
    mensajes_exito = {
        "registrado": "Paciente registrado correctamente.",
        "actualizado": "Paciente actualizado correctamente.",
        "eliminado": "Paciente eliminado correctamente."
    }

    # Obtener el mensaje correspondiente.
    for parametro, mensaje in mensajes_exito.items():
        if request.args.get(parametro):
            mensaje_exito = mensaje
            break

    # Identificar posibles errores.
    errores = {
        "conexion": "No fue posible conectar con la base de datos.",
        "no_encontrado": "El paciente que buscas no existe.",
        "relacionado": (
            "No se puede eliminar este paciente porque tiene "
            "citas médicas asociadas."
        ),
        "eliminacion": "No fue posible eliminar el paciente."
    }

    mensaje_error = errores.get(request.args.get("error"))

    # Establecer conexión con MySQL.
    conexion = get_connection()

    if conexion is None:
        mensaje_error = "No fue posible conectar con la base de datos."

        return render_template(
            "pacientes.html",
            pacientes=pacientes,
            mensaje_error=mensaje_error,
            mensaje_exito=mensaje_exito
        )

    cursor = None

    try:
        # Crear un cursor que devuelve los resultados como diccionarios.
        cursor = conexion.cursor(dictionary=True)

        # Consultar los pacientes registrados.
        consulta = """
            SELECT
                id_paciente,
                nombres,
                apellidos,
                documento,
                fecha_nacimiento,
                telefono,
                correo,
                direccion
            FROM paciente
            ORDER BY apellidos, nombres
        """

        cursor.execute(consulta)
        pacientes = cursor.fetchall()

    except Error as error:
        mensaje_error = "Error al consultar los pacientes."
        print("Error de MySQL:", error)

    finally:
        # Cerrar el cursor y la conexión.
        if cursor is not None:
            cursor.close()

        conexion.close()

    return render_template(
        "pacientes.html",
        pacientes=pacientes,
        mensaje_error=mensaje_error,
        mensaje_exito=mensaje_exito
    )


# =====================================================
# REGISTRAR PACIENTE
# =====================================================
@paciente_bp.route("/pacientes/nuevo", methods=["GET", "POST"])
def registrar_paciente():

    if request.method == "POST":

        # Obtener los datos enviados desde el formulario.
        nombres = request.form.get("nombres", "").strip()
        apellidos = request.form.get("apellidos", "").strip()
        documento = request.form.get("documento", "").strip()
        fecha_nacimiento = request.form.get("fecha_nacimiento", "")
        telefono = request.form.get("telefono", "").strip()
        correo = request.form.get("correo", "").strip()
        direccion = request.form.get("direccion", "").strip()

        # Validar los campos obligatorios.
        if not all([
            nombres,
            apellidos,
            documento,
            fecha_nacimiento,
            telefono,
            correo
        ]):
            return render_template(
                "formulario_paciente.html",
                mensaje_error="Completa todos los campos obligatorios."
            )

        # Establecer conexión con MySQL.
        conexion = get_connection()

        if conexion is None:
            return render_template(
                "formulario_paciente.html",
                mensaje_error="No fue posible conectar con la base de datos."
            )

        cursor = None

        try:
            cursor = conexion.cursor()

            # Consulta SQL para insertar un paciente.
            consulta = """
                INSERT INTO paciente (
                    nombres,
                    apellidos,
                    documento,
                    fecha_nacimiento,
                    telefono,
                    correo,
                    direccion
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            valores = (
                nombres,
                apellidos,
                documento,
                fecha_nacimiento,
                telefono,
                correo,
                direccion if direccion else None
            )

            cursor.execute(consulta, valores)

            # Confirmar el registro en la base de datos.
            conexion.commit()

            return redirect(
                url_for(
                    "pacientes.listar_pacientes",
                    registrado=1
                )
            )

        except Error as error:
            conexion.rollback()

            if error.errno == 1062:
                mensaje_error = (
                    "El documento o el correo ya se encuentra registrado."
                )
            else:
                mensaje_error = "No fue posible registrar el paciente."
                print("Error de MySQL:", error)

            return render_template(
                "formulario_paciente.html",
                mensaje_error=mensaje_error
            )

        finally:
            if cursor is not None:
                cursor.close()

            conexion.close()

    # Mostrar el formulario cuando se accede mediante GET.
    return render_template("formulario_paciente.html")


# =====================================================
# EDITAR PACIENTE
# =====================================================
@paciente_bp.route(
    "/pacientes/editar/<int:id_paciente>",
    methods=["GET", "POST"]
)
def editar_paciente(id_paciente):

    # Establecer conexión con MySQL.
    conexion = get_connection()

    if conexion is None:
        return "No fue posible conectar con la base de datos.", 500

    cursor = None
    paciente = None

    try:
        cursor = conexion.cursor(dictionary=True)

        # Buscar el paciente por su identificador.
        consulta = """
            SELECT
                id_paciente,
                nombres,
                apellidos,
                documento,
                fecha_nacimiento,
                telefono,
                correo,
                direccion
            FROM paciente
            WHERE id_paciente = %s
        """

        cursor.execute(consulta, (id_paciente,))
        paciente = cursor.fetchone()

        # Comprobar que el paciente exista.
        if paciente is None:
            return "El paciente no existe.", 404

        if request.method == "POST":

            # Obtener los nuevos datos del formulario.
            nombres = request.form.get("nombres", "").strip()
            apellidos = request.form.get("apellidos", "").strip()
            documento = request.form.get("documento", "").strip()
            fecha_nacimiento = request.form.get("fecha_nacimiento", "")
            telefono = request.form.get("telefono", "").strip()
            correo = request.form.get("correo", "").strip()
            direccion = request.form.get("direccion", "").strip()

            # Validar los campos obligatorios.
            if not all([
                nombres,
                apellidos,
                documento,
                fecha_nacimiento,
                telefono,
                correo
            ]):
                return render_template(
                    "editar_paciente.html",
                    paciente=paciente,
                    mensaje_error="Completa todos los campos obligatorios."
                )

            # Actualizar la información del paciente.
            consulta = """
                UPDATE paciente
                SET
                    nombres = %s,
                    apellidos = %s,
                    documento = %s,
                    fecha_nacimiento = %s,
                    telefono = %s,
                    correo = %s,
                    direccion = %s
                WHERE id_paciente = %s
            """

            valores = (
                nombres,
                apellidos,
                documento,
                fecha_nacimiento,
                telefono,
                correo,
                direccion if direccion else None,
                id_paciente
            )

            cursor.execute(consulta, valores)

            # Guardar los cambios en MySQL.
            conexion.commit()

            return redirect(
                url_for(
                    "pacientes.listar_pacientes",
                    actualizado=1
                )
            )

        # Mostrar el formulario con los datos actuales.
        return render_template(
            "editar_paciente.html",
            paciente=paciente
        )

    except Error as error:
        conexion.rollback()

        if error.errno == 1062:
            mensaje_error = (
                "El documento o correo ya pertenece a otro paciente."
            )
        else:
            mensaje_error = "No fue posible actualizar el paciente."
            print("Error de MySQL:", error)

        return render_template(
            "editar_paciente.html",
            paciente=paciente,
            mensaje_error=mensaje_error
        )

    finally:
        if cursor is not None:
            cursor.close()

        conexion.close()


# =====================================================
# ELIMINAR PACIENTE
# =====================================================
@paciente_bp.route(
    "/pacientes/eliminar/<int:id_paciente>",
    methods=["POST"]
)
def eliminar_paciente(id_paciente):

    # Establecer conexión con MySQL.
    conexion = get_connection()

    if conexion is None:
        return redirect(
            url_for(
                "pacientes.listar_pacientes",
                error="conexion"
            )
        )

    cursor = None

    try:
        cursor = conexion.cursor()

        # Eliminar el paciente utilizando su identificador.
        consulta = """
            DELETE FROM paciente
            WHERE id_paciente = %s
        """

        cursor.execute(consulta, (id_paciente,))

        # Verificar si se encontró el registro.
        if cursor.rowcount == 0:
            return redirect(
                url_for(
                    "pacientes.listar_pacientes",
                    error="no_encontrado"
                )
            )

        # Confirmar la eliminación en MySQL.
        conexion.commit()

        return redirect(
            url_for(
                "pacientes.listar_pacientes",
                eliminado=1
            )
        )

    except Error as error:
        # Revertir la operación si ocurre un error.
        conexion.rollback()

        # Error 1451: existen registros relacionados.
        if error.errno == 1451:
            return redirect(
                url_for(
                    "pacientes.listar_pacientes",
                    error="relacionado"
                )
            )

        print("Error de MySQL al eliminar:", error)

        return redirect(
            url_for(
                "pacientes.listar_pacientes",
                error="eliminacion"
            )
        )

    finally:
        if cursor is not None:
            cursor.close()

        conexion.close()
