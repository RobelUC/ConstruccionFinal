"""
Interfaz gráfica del Gestor de Tareas desarrollada con Flet.
Maneja la visualización de pantallas, la comunicación con el controlador y el feedback de errores.
"""

from src.logica.task_manager import TaskManager
import flet as ft
import sys
import os

# --- CONFIGURACIÓN DE RUTAS ---
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

    # Inicialización del controlador
    manager = TaskManager()

    # ---------------------------------------------------------
    # VISTA: LOGIN
    # ---------------------------------------------------------
    def mostrar_login():
        page.clean()

        email = ft.TextField(label="Correo Electrónico", width=280)
        password = ft.TextField(label="Contraseña", password=True, width=280)

        def funcion_entrar(e):
            """Valida los campos e intenta iniciar sesión."""
            if not email.value or not password.value:
                page.snack_bar = ft.SnackBar(
                    ft.Text("Por favor, ingrese todos los datos"))
                page.snack_bar.open = True
                page.update()
                return

            try:
                # Intentamos loguear
                usuario = manager.login(email.value, password.value)

                # Si llegamos aquí, el login fue exitoso
                mostrar_exito(usuario)

            except ValueError as error:
                # 1. Errores de Validación (Correo no existe / Clave mal)
                page.snack_bar = ft.SnackBar(
                    ft.Text(str(error)),
                    bgcolor="orange"
                )
                page.snack_bar.open = True
                page.update()

            except Exception as error:
                # 2. Errores Inesperados (Base de datos, código, etc.)
                # ESTO ES LO QUE AGREGUÉ PARA MAYOR SEGURIDAD
                print(f"Error crítico: {error}")  # Para ver en consola
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"Error del sistema: {str(error)}"),
                    bgcolor="red"
                )
                page.snack_bar.open = True
                page.update()

        def ir_registro(e):
            mostrar_registro()

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
            if not txt_email.value or not txt_pass.value or not txt_nombre.value:
                page.snack_bar = ft.SnackBar(
                    ft.Text("Complete los campos obligatorios"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                return

            try:
                exito = manager.registrar_usuario(
                    email=txt_email.value,
                    password=txt_pass.value,
                    nombre=txt_nombre.value
                )

                if exito:
                    page.snack_bar = ft.SnackBar(
                        ft.Text("¡Usuario Creado!"), bgcolor="green")
                    page.snack_bar.open = True
                    mostrar_login()
                else:
                    page.snack_bar = ft.SnackBar(
                        ft.Text("Error: El correo ya está registrado"), bgcolor="red")
                    page.snack_bar.open = True
                    page.update()

            except Exception as error:
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"Error inesperado: {str(error)}"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

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
    # VISTA: PANEL PRINCIPAL
    # ---------------------------------------------------------
    def mostrar_exito(usuario):
        page.clean()
        page.add(
            ft.Column(
                [
                    ft.Text("✅", size=100),
                    ft.Text(f"¡Hola {usuario.nombre}!",
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

    mostrar_login()


if __name__ == "__main__":
    ft.app(target=main)
