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
    page.window_height = 650
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

        # Función para cerrar la alerta de error
        def cerrar_dialogo(e):
            page.dialog.open = False
            page.update()

        def funcion_entrar(e):
            # 1. Limpieza total de estados previos
            email.error_text = None
            password.error_text = None
            page.dialog = None # Limpiamos cualquier diálogo viejo
            page.update()

            try:
                print(f"Intentando login para: {email.value}")
                usuario = manager.login(email.value, password.value)
                print("Login exitoso")
                mostrar_exito(usuario)

            except ValueError as err:
                print(f"ERROR CAPTURADO: {err}")
                
                # Creamos el diálogo de forma independiente
                alerta = ft.AlertDialog(
                    modal=True, # Obliga al usuario a interactuar
                    title=ft.Text("⚠️ Error de Acceso"),
                    content=ft.Text(str(err)),
                    actions=[
                        ft.TextButton("Entendido", on_click=cerrar_dialogo)
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                
                # ASIGNACIÓN Y APERTURA FORZADA
                page.dialog = alerta
                alerta.open = True
                page.update()

            except Exception as ex:
                print(f"FALLO CRÍTICO: {ex}")
                page.snack_bar = ft.SnackBar(ft.Text("Error de sistema"))
                page.snack_bar.open = True
                page.update()
                
        def ir_registro(e):
            mostrar_registro()

        page.add(
            ft.Column(
                [
                    ft.Text("🔐", size=80),  # TUS ICONOS ORIGINALES
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
                    ft.Text("📝", size=60), # TUS ICONOS ORIGINALES
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
                    ft.Text("✅", size=100), # TUS ICONOS ORIGINALES
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