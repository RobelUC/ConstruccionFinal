"""
Interfaz gráfica del Gestor de Tareas desarrollada con Flet.
Maneja la visualización de pantallas y la comunicación con el controlador.
"""

from src.logica.task_manager import TaskManager
import flet as ft
import sys
import os

# --- CONFIGURACIÓN DE RUTAS ---
# Permite que el script encuentre el paquete 'src' sin importar el directorio de ejecución.
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'src')))


def main(page: ft.Page):
    """
    Configuración inicial de la ventana y ruteo de pantallas.
    """
    page.title = "Paso 1: Acceso"
    page.window_width = 400
    page.window_height = 600
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT

    # Inicialización del controlador y la base de datos
    manager = TaskManager()
    try:
        manager.inicializar_db()
        print("Base de datos conectada correctamente.")
    except Exception as e:
        page.add(ft.Text(f"Error conectando BD: {e}", color="red"))

    # ---------------------------------------------------------
    # VISTA: LOGIN
    # ---------------------------------------------------------
    def mostrar_login():
        """
        Renderiza el formulario de acceso y gestiona la validación de credenciales.
        """
        page.clean()

        email = ft.TextField(label="Correo Electrónico", width=280)
        password = ft.TextField(label="Contraseña", password=True, width=280)

        def funcion_entrar(e):
            """Valida los campos e intenta iniciar sesión."""
            if not email.value or not password.value:
                page.snack_bar = ft.SnackBar(ft.Text("Faltan datos"))
                page.snack_bar.open = True
                page.update()
                return

            user_id = manager.login(email.value, password.value)

            if user_id:
                mostrar_exito(user_id)
            else:
                page.snack_bar = ft.SnackBar(
                    ft.Text("Correo o clave incorrectos"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

        def ir_registro(e):
            mostrar_registro()

        # Layout de la pantalla de login
        page.add(
            ft.Column(
                [
                    ft.Text("🔐", size=80),
                    ft.Text("Bienvenido", size=30, weight="bold"),
                    ft.Container(height=20),
                    email,
                    password,
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "INGRESAR", on_click=funcion_entrar, width=280),
                    ft.TextButton("Crear cuenta nueva", on_click=ir_registro)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        page.update()

    # ---------------------------------------------------------
    # VISTA: REGISTRO
    # ---------------------------------------------------------
    def mostrar_registro():
        """
        Formulario de creación de nuevos usuarios.
        """
        page.clean()

        txt_nombre = ft.TextField(label="Nombre", width=280)
        txt_apellido = ft.TextField(label="Apellido", width=280)
        txt_email = ft.TextField(label="Email", width=280)
        txt_pass = ft.TextField(label="Contraseña", password=True, width=280)
        txt_fecha = ft.TextField(
            label="Fecha Nacimiento (DD/MM/AAAA)", width=280)

        dd_genero = ft.Dropdown(
            width=280,
            label="Género",
            options=[ft.dropdown.Option("M"), ft.dropdown.Option("F")]
        )

        def funcion_guardar(e):
            """Envía los datos al backend para el registro."""
            try:
                manager.registrar_usuario(
                    txt_email.value, txt_pass.value, txt_nombre.value,
                    txt_apellido.value, txt_fecha.value, dd_genero.value
                )
                page.snack_bar = ft.SnackBar(
                    ft.Text("¡Usuario Creado!"), bgcolor="green")
                page.snack_bar.open = True
                mostrar_login()

            except ValueError as error:
                page.snack_bar = ft.SnackBar(
                    ft.Text(str(error)), bgcolor="red")
                page.snack_bar.open = True
                page.update()

        # Layout de la pantalla de registro
        page.add(
            ft.Column(
                [
                    ft.Text("📝", size=60),
                    ft.Text("Crear Cuenta", size=25, weight="bold"),
                    txt_nombre, txt_apellido, txt_email, txt_pass, txt_fecha, dd_genero,
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "REGISTRARME", on_click=funcion_guardar, width=280, bgcolor="green", color="white"),
                    ft.TextButton("Volver", on_click=lambda e: mostrar_login())
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO
            )
        )
        page.update()

    # ---------------------------------------------------------
    # VISTA: PANEL PRINCIPAL (SUCCESS)
    # ---------------------------------------------------------
    def mostrar_exito(user_id):
        """
        Pantalla de confirmación tras un login exitoso.
        """
        page.clean()
        page.add(
            ft.Column(
                [
                    ft.Text("✅", size=100),
                    ft.Text(f"¡Hola Usuario {user_id}!",
                            size=30, weight="bold", color="green"),
                    ft.Text("Has iniciado sesión correctamente."),
                    ft.Divider(),
                    ft.Text("El Paso 1 está completado.", size=20),
                    ft.ElevatedButton(
                        "Cerrar Sesión", on_click=lambda e: mostrar_login())
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        page.update()

    # Inicio de la aplicación
    mostrar_login()


if __name__ == "__main__":
    ft.app(target=main)
