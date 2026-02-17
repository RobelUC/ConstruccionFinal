"""
Interfaz gráfica del Gestor de Tareas desarrollada con Flet.
Maneja la visualización de pantallas, la comunicación con el controlador y el feedback de errores.
"""

import flet as ft
import sys
import os
from flet import icons
import random

# Compatibilidad Flet
if not hasattr(ft, "colors"):
    ft.colors = ft.Colors

# --- CONFIGURACIÓN DE RUTAS ---
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'src')))

from src.logica.task_manager import TaskManager


def main(page: ft.Page):
    """
    Configuración inicial de la ventana y ruteo de pantallas.
    """
    page.title = "Paso 1: Acceso"
    page.window_width = 400
    page.window_height = 650
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT

    manager = TaskManager()

    # ---------------------------------------------------------
    # LOGIN
    # ---------------------------------------------------------
    def mostrar_login():
        page.clean()
        page.title = "Paso 1: Acceso"

        email = ft.TextField(label="Correo Electrónico", width=280)
        password = ft.TextField(label="Contraseña", password=True, width=280)
        
        # --- NUEVA ETIQUETA DE ERROR ---
        # Inicialmente oculta, se muestra solo si falla el login
        txt_error = ft.Text("", color="red", visible=False, size=14, weight="bold")

        def cerrar_dialogo(e):
            page.dialog.open = False
            page.update()

        def funcion_entrar(e):
            # Reiniciar estados de error
            email.error_text = None
            password.error_text = None
            txt_error.visible = False
            page.update()

            try:
                usuario = manager.login(email.value, password.value)
                
                # Si el manager devuelve None (usuario no encontrado) y no lanza error:
                if not usuario:
                     raise ValueError("Correo o contraseña incorrectos")

                mostrar_tareas(usuario)

            except ValueError as err:
                # --- AQUÍ SE ACTIVA LA ETIQUETA ---
                txt_error.value = f"⚠️ {str(err)}"
                txt_error.visible = True
                page.update()

            except Exception:
                page.snack_bar = ft.SnackBar(ft.Text("Error de sistema"))
                page.snack_bar.open = True
                page.update()

        page.add(
            ft.Column(
                [
                    ft.Text("🔐", size=80),
                    ft.Text("Bienvenido", size=30, weight="bold"),
                    ft.Container(height=20),
                    email,
                    password,
                    # Agregamos la etiqueta de error al diseño
                    txt_error,
                    ft.Container(height=20),
                    ft.ElevatedButton("INGRESAR", on_click=funcion_entrar, width=280),
                    ft.TextButton("Crear cuenta nueva", on_click=lambda e: mostrar_registro())
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        page.update()

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
# LISTAR TAREAS (VERSIÓN MEJORADA Y MEJORADA)
# ---------------------------------------------------------
    def mostrar_tareas(usuario):
        page.clean()
        page.title = "Mis Tareas"
        page.padding = 30
        page.bgcolor = ft.colors.WHITE

        frases = [
            "La disciplina supera la motivación ",
            "Hoy es un gran día para avanzar 💡",
            "Pequeños pasos, grandes resultados 🚀"
        ]

        buscador = ft.TextField(label="Buscar tarea", width=300, hint_text="Buscar por título o fecha")

        filtro = ft.Dropdown(
            label="Filtrar por estado",
            width=200,
            value="Todas",
            options=[
                ft.dropdown.Option("Todas"),
                ft.dropdown.Option("Pendiente"),
                ft.dropdown.Option("Completada")
            ]
        )

        lista = ft.Column(
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO
        )

        # ---------- FUNCION GLOBAL PARA CERRAR DIALOGO ----------
        def ver_descripcion(e, tarea):

            dialogo = ft.AlertDialog(
                modal=True,
                title=ft.Text(tarea["titulo"]),
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.Text("📌 Descripción:", weight=ft.FontWeight.BOLD),
                        ft.Text(tarea.get("descripcion", "Sin descripción")),
                        ft.Divider(),
                        ft.Text("⭐ Prioridad:", weight=ft.FontWeight.BOLD),
                        ft.Text(tarea.get("prioridad", "No definida")),
                    ]
                ),
                actions=[
                    ft.TextButton("Cerrar", on_click=lambda e: cerrar(dialogo))
                ]
            )

            page.overlay.append(dialogo)   # 👈 ESTA ES LA CLAVE
            dialogo.open = True
            page.update()


        def cerrar(dialogo):
            dialogo.open = False
            page.update()



        # ---------- RECARGAR LISTA ----------
        def cargar_tareas():
            lista.controls.clear()

            texto = buscador.value.strip().lower() if buscador.value else ""

            estado = None

            if filtro.value == "Pendiente":
                estado = "pendiente"
            elif filtro.value == "Completada":
                estado = "completada"

            tareas = manager.filtrar_tareas_usuario(usuario["id"], estado)

            if texto:
                tareas = [
                    t for t in tareas
                    if texto in t["titulo"].lower() or texto in t.get("fecha", "").lower()
                ]

            pendientes = [t for t in tareas if t["estado"] == "pendiente"]
            completadas = [t for t in tareas if t["estado"] == "completada"]

            if filtro.value == "Pendiente":
                completadas = []
            elif filtro.value == "Completada":
                pendientes = []

            lista.controls.append(
                ft.Text(
                    f"Total: {len(tareas)} | Pendientes: {len(pendientes)} | Completadas: {len(completadas)}",
                    size=13,
                    color=ft.colors.GREY_700
                )
            )
            lista.controls.append(ft.Divider())

            # ---------- PENDIENTES ----------
            lista.controls.append(ft.Text("Pendientes", weight=ft.FontWeight.BOLD, size=18))

            for t in pendientes:
                lista.controls.append(
                    ft.Container(
                        padding=10,
                        margin=5,
                        bgcolor=ft.colors.GREY_100,
                        border_radius=12,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Checkbox(
                                            value=False,
                                            on_change=lambda e, id=t["id"]: cambiar_estado(id)
                                        ),
                                        ft.Column(
                                            spacing=2,
                                            controls=[
                                                ft.Text(t["titulo"], weight=ft.FontWeight.BOLD, size=14),
                                                ft.Text(f"Fecha: {t.get('fecha', 'Sin fecha')}", size=12, color=ft.colors.GREY_700),
                                                ft.TextButton(
                                                    "Ver descripción",
                                                    on_click=lambda e, tarea=t: ver_descripcion(e, tarea),
                                                    style=ft.ButtonStyle(
                                                        text_style=ft.TextStyle(color=ft.colors.BLUE)
                                                    )
                                                )
                                            ]
                                        )
                                    ]
                                ),
                                ft.Row(
                                    spacing=5,
                                    controls=[
                                        ft.ElevatedButton(
                                            "✏️",
                                            width=40,
                                            height=40,
                                            on_click=lambda e, tarea=t: mostrar_editar(usuario, tarea)
                                        ),
                                        ft.ElevatedButton(
                                            "❌",
                                            bgcolor=ft.colors.RED,
                                            color=ft.colors.WHITE,
                                            width=40,
                                            height=40,
                                            on_click=lambda e, id=t["id"]: eliminar(id)
                                        )
                                    ]
                                )
                            ]
                        )
                    )
                )

            # ---------- COMPLETADAS ----------
            lista.controls.append(ft.Divider())
            lista.controls.append(ft.Text("Completadas", weight=ft.FontWeight.BOLD, size=18))

            for t in completadas:
                lista.controls.append(
                    ft.Container(
                        padding=10,
                        margin=5,
                        bgcolor=ft.colors.GREEN_50,
                        border_radius=12,
                        content=ft.Row(
                            controls=[
                                ft.Text("✔", size=20, color=ft.colors.GREEN),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(t["titulo"], size=14, italic=True),
                                        ft.Text(f"Fecha: {t.get('fecha', 'Sin fecha')}", size=12, color=ft.colors.GREY_700),
                                        ft.TextButton(
                                            "Ver descripción",
                                            on_click=lambda e, tarea=t: ver_descripcion(e, tarea),
                                            style=ft.ButtonStyle(
                                                text_style=ft.TextStyle(color=ft.colors.BLUE)
                                            )
                                        )
                                    ]
                                )
                            ]
                        )
                    )
                )

            page.update()

        # ---------- CAMBIAR ESTADO ----------
        def cambiar_estado(id_task):
            manager.marcar_completada(id_task)
            cargar_tareas()

        # ---------- ELIMINAR ----------
        def eliminar(id_task):
            manager.eliminar_tarea(id_task)
            cargar_tareas()

        # ---------- HEADER ----------
        header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text("Mis Tareas", size=24, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton(
                    "Cerrar sesión",
                    on_click=lambda e: mostrar_login()
                )
            ]
        )

        saludo = ft.Text(f"Hola, {usuario['nombre']} 👋")
        motivacion = ft.Text(random.choice(frases), color=ft.colors.PURPLE)

        buscador.on_change = lambda e: cargar_tareas()
        filtro.on_change = lambda e: cargar_tareas()

        page.add(
            header,
            ft.Divider(),
            saludo,
            motivacion,
            buscador,
            filtro,
            ft.ElevatedButton(
                "➕ Nueva tarea",
                bgcolor=ft.colors.BLACK,
                color=ft.colors.WHITE,
                on_click=lambda e: mostrar_crear(usuario)
            ),
            ft.Divider(),
            lista
        )

        cargar_tareas()


# ---------------------------------------------------------
# CREAR TAREA
# ---------------------------------------------------------
    def mostrar_crear(usuario):

        page.clean()
        page.title = "Crear Tarea"

        txt_titulo = ft.TextField(label="Título")
        txt_descripcion = ft.TextField(label="Descripción", multiline=True)
        txt_fecha = ft.TextField(label="Fecha (dd/mm/aaaa)")
        prioridad = ft.Dropdown(
            label="Prioridad",
            value="Media",
            options=[
                ft.dropdown.Option("Alta"),
                ft.dropdown.Option("Media"),
                ft.dropdown.Option("Baja")
            ]
        )

        mensaje = ft.Text("", color="red")

        def guardar(e):

            # Limpiar errores previos
            txt_titulo.error_text = None
            txt_descripcion.error_text = None
            txt_fecha.error_text = None
            mensaje.value = ""

            titulo = txt_titulo.value.strip() if txt_titulo.value else ""
            descripcion = txt_descripcion.value.strip() if txt_descripcion.value else ""
            fecha = txt_fecha.value.strip() if txt_fecha.value else ""

            error = False

            # Validaciones
            if not titulo:
                txt_titulo.error_text = "El título es obligatorio"
                error = True

            if not descripcion:
                txt_descripcion.error_text = "La descripción es obligatoria"
                error = True

            if not fecha:
                txt_fecha.error_text = "La fecha es obligatoria"
                error = True

            if error:
                mensaje.value = "Complete todos los campos obligatorios"
                mensaje.color = "red"
                page.update()
                return

            # Guardar tarea
            manager.agregar_tarea_usuario(
                user_id=usuario["id"],
                titulo=titulo,
                descripcion=descripcion,
                fecha=fecha,
                prioridad=prioridad.value
            )

            # Mostrar mensaje de éxito
            mensaje.value = "✅ La tarea fue creada correctamente"
            mensaje.color = "green"

            # Limpiar campos
            txt_titulo.value = ""
            txt_descripcion.value = ""
            txt_fecha.value = ""
            prioridad.value = "Media"

            page.update()

        page.add(
            ft.Text("Crear Tarea", size=22, weight="bold"),
            txt_titulo,
            txt_descripcion,
            txt_fecha,
            prioridad,
            mensaje,
            ft.Row(
                [
                    ft.ElevatedButton("Guardar", on_click=guardar),
                    ft.TextButton("Cancelar", on_click=lambda e: mostrar_tareas(usuario))
                ]
            )
        )

        page.update()



# --------------------------------------------------------- 
# EDITAR TAREA
# ---------------------------------------------------------
    def mostrar_editar(usuario, tarea):
        page.clean()
        page.title = "Editar Tarea"

        # Cambiar .titulo -> ["titulo"], .descripcion -> ["descripcion"], etc.
        titulo = ft.TextField(label="Título", value=tarea["titulo"])
        descripcion = ft.TextField(label="Descripción", value=tarea["descripcion"], multiline=True)
        fecha = ft.TextField(label="Fecha", value=tarea.get("fecha", ""))  # .get para evitar error si no hay fecha
        prioridad = ft.Dropdown(
            label="Prioridad",
            value=tarea.get("prioridad", "Media"),
            options=[
                ft.dropdown.Option("Alta"),
                ft.dropdown.Option("Media"),
                ft.dropdown.Option("Baja")
            ]
        )

        def guardar(e):
            # Usar diccionario con llaves
            manager.editar_tarea(
                tarea["id"],
                titulo.value,
                descripcion.value,
                fecha.value,
                prioridad.value
            )
            mostrar_tareas(usuario)

        page.add(
            ft.Text("Editar Tarea", size=22, weight="bold"),
            titulo,
            descripcion,
            fecha,
            prioridad,
            ft.ElevatedButton("Guardar", on_click=guardar),
            ft.TextButton("Cancelar", on_click=lambda e: mostrar_tareas(usuario))
        )

        page.update()


    # INICIO
    mostrar_login()


if __name__ == "__main__":
    ft.app(target=main)