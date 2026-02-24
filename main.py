"""
Interfaz gráfica del Gestor de Tareas (Flet).
Controla el ruteo de vistas, la comunicación con el TaskManager y las validaciones de UI.
"""

from src.logica.task_manager import TaskManager
import flet as ft
import sys
import os
import random
from datetime import datetime

# Parche de compatibilidad para versiones recientes de Flet
if not hasattr(ft, "colors"):
    ft.colors = ft.Colors

# Agregar 'src' al path para permitir la importación de módulos internos
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'src')))

# ==========================================
# COMPONENTES REUTILIZABLES
# ==========================================


def crear_componente_fecha(page: ft.Page, valor_inicial=""):
    """Genera un TextField acoplado a un DatePicker para estandarizar el ingreso de fechas."""
    txt_fecha = ft.TextField(label="Fecha (dd/mm/aaaa)", value=valor_inicial)

    def fecha_seleccionada(e):
        if date_picker.value:
            txt_fecha.value = date_picker.value.strftime("%d/%m/%Y")
            txt_fecha.error_text = None
            page.update()

    date_picker = ft.DatePicker(
        first_date=datetime(2000, 1, 1),
        last_date=datetime(2100, 12, 31),
        on_change=fecha_seleccionada
    )
    page.overlay.append(date_picker)

    def abrir_calendario(e):
        try:
            if txt_fecha.value:
                date_picker.value = datetime.strptime(
                    txt_fecha.value, "%d/%m/%Y")
            else:
                date_picker.value = datetime.now()
        except ValueError:
            date_picker.value = datetime.now()

        date_picker.open = True
        page.update()

    icono_calendario = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH,
        tooltip="Abrir calendario",
        on_click=abrir_calendario
    )

    fila_fecha = ft.Row(
        controls=[txt_fecha, icono_calendario],
        alignment=ft.MainAxisAlignment.START,
        spacing=10
    )

    return txt_fecha, fila_fecha


# ==========================================
# VISTAS (PANTALLAS)
# ==========================================

def mostrar_login(page: ft.Page, manager: TaskManager):
    page.clean()
    page.title = "Acceso"

    email = ft.TextField(label="Correo Electrónico", width=280)
    password = ft.TextField(label="Contraseña", password=True, width=280)
    txt_error = ft.Text("", color="red", visible=False, size=14, weight="bold")

    def funcion_entrar(e):
        email.error_text, password.error_text = None, None
        txt_error.visible = False
        page.update()

        try:
            usuario = manager.login(email.value, password.value)
            if not usuario:
                raise ValueError("Correo o contraseña incorrectos")

            mostrar_tareas(page, manager, usuario)

        except ValueError as err:
            txt_error.value = f"⚠️ {str(err)}"
            txt_error.visible = True
            page.update()
        except Exception:
            mostrar_snackbar(page, "Error de sistema", "red")

    page.add(
        ft.Column(
            [
                ft.Text("🔐", size=80),
                ft.Text("Bienvenido", size=30, weight="bold"),
                ft.Container(height=20),
                email,
                password,
                txt_error,
                ft.Container(height=20),
                ft.ElevatedButton(
                    "INGRESAR", on_click=funcion_entrar, width=280),
                ft.TextButton("Crear cuenta nueva",
                              on_click=lambda e: mostrar_registro(page, manager))
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
    page.update()


def mostrar_registro(page: ft.Page, manager: TaskManager):
    page.clean()
    page.title = "Registro"

    txt_nombre = ft.TextField(label="Nombre", width=280)
    txt_apellido = ft.TextField(label="Apellido", width=280)
    txt_email = ft.TextField(label="Email", width=280)
    txt_pass = ft.TextField(label="Contraseña", password=True, width=280)
    txt_fecha = ft.TextField(label="Fecha Nacimiento (DD/MM/AAAA)",
                             width=280, hint_text="Ej: 25/12/2000", max_length=10)
    dd_genero = ft.Dropdown(width=280, label="Género", options=[
                            ft.dropdown.Option("M"), ft.dropdown.Option("F")])
    mensaje = ft.Text("", color="red")

    def funcion_guardar(e):
        for campo in [txt_nombre, txt_email, txt_pass, txt_fecha]:
            campo.error_text = None
        mensaje.value = ""
        page.update()

        error = False
        email_text = txt_email.value.strip() if txt_email.value else ""
        fecha_text = txt_fecha.value.strip() if txt_fecha.value else ""

        if not txt_nombre.value or not txt_nombre.value.strip():
            txt_nombre.error_text = "Obligatorio"
            error = True

        if not email_text or "@" not in email_text or "." not in email_text or " " in email_text:
            txt_email.error_text = "Correo no válido"
            error = True

        if not txt_pass.value or not txt_pass.value.strip():
            txt_pass.error_text = "Obligatoria"
            error = True

        try:
            if not fecha_text or datetime.strptime(fecha_text, "%d/%m/%Y") > datetime.now():
                raise ValueError
        except ValueError:
            txt_fecha.error_text = "Fecha no válida"
            error = True

        if error:
            mensaje.value = "Complete los campos correctamente"
            page.update()
            return

        try:
            exito = manager.registrar_usuario(
                email=email_text,
                password=txt_pass.value,
                nombre=txt_nombre.value
            )

            if exito:
                mensaje.value = "✅ ¡Cuenta creada con éxito!"
                mensaje.color = ft.colors.GREEN
                e.control.disabled = True

                page.snack_bar = ft.SnackBar(
                    content=ft.Text("🎉 ¡Bienvenido! Redirigiendo..."),
                    bgcolor=ft.colors.GREEN_700,
                    duration=2000
                )
                page.snack_bar.open = True
                page.update()

                import threading

                def finalizar():
                    mostrar_login(page, manager)

                threading.Timer(2.0, finalizar).start()

            else:
                mensaje.value = "Error: No se pudo guardar en la base de datos"
                page.update()

        except ValueError as err:
            txt_email.error_text = str(err)
            mensaje.value = "El usuario ya existe"
            mensaje.color = ft.colors.RED
            page.update()

        except Exception as error_db:
            mostrar_snackbar(page, f"Error inesperado: {str(error_db)}", "red")

    page.add(
        ft.Column(
            [
                ft.Text("📝", size=60),
                ft.Text("Crear Cuenta", size=25, weight="bold"),
                txt_nombre, txt_apellido, txt_email, txt_pass, txt_fecha, dd_genero, mensaje,
                ft.Container(height=10),
                ft.ElevatedButton("REGISTRARME", on_click=funcion_guardar,
                                  width=280, bgcolor="green", color="white"),
                ft.TextButton(
                    "Volver", on_click=lambda e: mostrar_login(page, manager))
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO
        )
    )
    page.update()


def mostrar_tareas(page: ft.Page, manager: TaskManager, usuario: dict):
    page.clean()
    page.title = "Mis Tareas"
    page.padding = 30
    page.bgcolor = ft.colors.WHITE

    frases = ["La disciplina supera la motivación 💪",
              "Hoy es un gran día para avanzar 💡", "Pequeños pasos, grandes resultados 🚀"]

    buscador = ft.TextField(label="Buscar tarea", width=300,
                            hint_text="Buscar por título o fecha")
    filtro = ft.Dropdown(label="Filtrar por estado", width=200, value="Todas", options=[
                         ft.dropdown.Option("Todas"), ft.dropdown.Option("Pendiente"), ft.dropdown.Option("Completada")])

    lista = ft.Column(spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)

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
            actions=[ft.TextButton(
                "Cerrar", on_click=lambda e: cerrar_dialogo(dialogo))]
        )
        page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

    def cerrar_dialogo(dialogo):
        dialogo.open = False
        page.update()

    def cargar_tareas(e=None):
        lista.controls.clear()

        texto = buscador.value.strip().lower() if buscador.value else ""

        # Obtener tareas y ordenarlas de más reciente a más antigua
        tareas_raw = manager.listar_tareas_usuario(usuario["id"])
        tareas_ordenadas = sorted(
            tareas_raw,
            key=lambda t: datetime.strptime(
                t.get('fecha', '01/01/2000'), "%d/%m/%Y"),
            reverse=True
        )

        # Aplicar búsqueda si hay texto ingresado
        if texto:
            tareas_finales = [t for t in tareas_ordenadas if texto in t["titulo"].lower()
                              or texto in t.get("fecha", "").lower()]
        else:
            tareas_finales = tareas_ordenadas

        pendientes = [t for t in tareas_finales if t["estado"] == "pendiente"]
        completadas = [
            t for t in tareas_finales if t["estado"] == "completada"]

        # --- SECCIÓN PENDIENTES ---
        lista.controls.append(
            ft.Text("Pendientes", weight=ft.FontWeight.BOLD, size=18))

        if pendientes:
            for t in pendientes:
                lista.controls.append(
                    crear_tarjeta_tarea(t, es_completada=False))
        else:
            msj = "🔍 No se encontraron coincidencias." if texto else "🌟 ¡No tienes tareas pendientes! Estás al día."
            lista.controls.append(ft.Container(content=ft.Text(
                msj, italic=True, color=ft.colors.GREY_600), padding=10))

        lista.controls.append(ft.Divider())

        # --- SECCIÓN COMPLETADAS ---
        lista.controls.append(
            ft.Text("Completadas", weight=ft.FontWeight.BOLD, size=18))

        if completadas:
            for t in completadas:
                lista.controls.append(
                    crear_tarjeta_tarea(t, es_completada=True))
        else:
            msj_comp = "No hay resultados en completadas." if texto else "Aún no has terminado tareas."
            lista.controls.append(
                ft.Text(msj_comp, color=ft.colors.GREY_500, size=14))

        page.update()

    def crear_tarjeta_tarea(t, es_completada):
        color_bg = ft.colors.GREEN_50 if es_completada else ft.colors.GREY_100
        icono_estado = ft.Text("✔", size=20, color=ft.colors.GREEN) if es_completada else ft.Checkbox(
            value=False, on_change=lambda e: cambiar_estado(t["id"]))

        return ft.Container(
            padding=10, margin=5, bgcolor=color_bg, border_radius=12,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(controls=[
                        icono_estado,
                        ft.Column(spacing=2, controls=[
                            ft.Text(
                                t["titulo"],
                                weight=ft.FontWeight.BOLD if not es_completada else ft.FontWeight.NORMAL,
                                size=14,
                                italic=es_completada
                            ),
                            ft.Text(
                                f"Fecha: {t.get('fecha', 'Sin fecha')}",
                                size=12, color=ft.colors.GREY_700
                            ),
                            ft.TextButton(
                                "Ver descripción", on_click=lambda e: ver_descripcion(e, t))
                        ])
                    ]),
                    ft.Row(spacing=5, controls=[
                        # Ocultar botón de edición en tareas que ya están finalizadas
                        ft.ElevatedButton("✏️", width=40, height=40,
                                          on_click=lambda e: mostrar_editar(page, manager, usuario, t)) if not es_completada else ft.Container(),

                        ft.ElevatedButton("❌", bgcolor=ft.colors.RED, color=ft.colors.WHITE,
                                          width=40, height=40, on_click=lambda e: eliminar(t["id"]))
                    ])
                ]
            )
        )

    def cambiar_estado(id_task):
        manager.marcar_completada(id_task)
        cargar_tareas()

    def eliminar(id_task):
        manager.eliminar_tarea(id_task)
        cargar_tareas()

    # Vincular recarga automática al escribir o cambiar el filtro
    buscador.on_change = cargar_tareas
    filtro.on_change = cargar_tareas

    header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Text("Mis Tareas", size=24, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                "Cerrar sesión", on_click=lambda e: mostrar_login(page, manager))
        ]
    )

    page.add(
        header, ft.Divider(),
        ft.Text(f"Hola, {usuario['nombre']} 👋"),
        ft.Text(random.choice(frases), color=ft.colors.PURPLE),
        buscador, filtro,
        ft.ElevatedButton("➕ Nueva tarea", bgcolor=ft.colors.BLACK, color=ft.colors.WHITE,
                          on_click=lambda e: mostrar_crear(page, manager, usuario)),
        ft.Divider(), lista
    )

    cargar_tareas()


def mostrar_crear(page: ft.Page, manager: TaskManager, usuario: dict):
    page.clean()
    page.title = "Crear Tarea"

    txt_titulo = ft.TextField(label="Título")
    txt_descripcion = ft.TextField(label="Descripción", multiline=True)
    prioridad = ft.Dropdown(label="Prioridad", value="Media", options=[ft.dropdown.Option(
        "Alta"), ft.dropdown.Option("Media"), ft.dropdown.Option("Baja")])
    mensaje = ft.Text("", color="red")

    txt_fecha, fila_fecha = crear_componente_fecha(page)

    def guardar(e):
        txt_titulo.error_text, txt_descripcion.error_text, txt_fecha.error_text = None, None, None
        mensaje.value = ""
        error = False

        if not txt_titulo.value:
            txt_titulo.error_text, error = "Obligatorio", True
        if not txt_descripcion.value:
            txt_descripcion.error_text, error = "Obligatorio", True
        if not txt_fecha.value:
            txt_fecha.error_text, error = "Obligatorio", True
        else:
            try:
                datetime.strptime(txt_fecha.value, "%d/%m/%Y")
            except ValueError:
                txt_fecha.error_text, error = "Formato inválido", True

        if error:
            mensaje.value, mensaje.color = "Complete los campos obligatorios", "red"
            page.update()
            return

        exito = manager.agregar_tarea_usuario(
            usuario["id"], txt_titulo.value, txt_descripcion.value, txt_fecha.value, prioridad.value)

        if exito:
            mostrar_snackbar(page, "✅ Tarea creada", "green")
            mostrar_tareas(page, manager, usuario)
        else:
            mensaje.value, mensaje.color = "Error al guardar", "red"
            page.update()

    page.add(
        ft.Text("Crear Tarea", size=22, weight="bold"),
        txt_titulo, txt_descripcion, fila_fecha, prioridad, mensaje,
        ft.Row([
            ft.ElevatedButton("Guardar", on_click=guardar),
            ft.TextButton("Cancelar", on_click=lambda e: mostrar_tareas(
                page, manager, usuario))
        ])
    )
    page.update()


def mostrar_editar(page: ft.Page, manager: TaskManager, usuario: dict, tarea: dict):
    page.clean()
    page.title = "Editar Tarea"

    txt_titulo = ft.TextField(label="Título", value=tarea["titulo"])
    txt_descripcion = ft.TextField(
        label="Descripción", value=tarea["descripcion"], multiline=True)
    prioridad = ft.Dropdown(label="Prioridad", value=tarea.get("prioridad", "Media"), options=[
                            ft.dropdown.Option("Alta"), ft.dropdown.Option("Media"), ft.dropdown.Option("Baja")])

    txt_fecha, fila_fecha = crear_componente_fecha(
        page, tarea.get("fecha", ""))

    def guardar_editar(e):
        if txt_fecha.value:
            try:
                datetime.strptime(txt_fecha.value, "%d/%m/%Y")
            except ValueError:
                txt_fecha.error_text = "Formato inválido. dd/mm/aaaa"
                page.update()
                return

        manager.editar_tarea(tarea["id"], txt_titulo.value,
                             txt_descripcion.value, txt_fecha.value, prioridad.value)
        mostrar_tareas(page, manager, usuario)

    page.add(
        ft.Text("Editar Tarea", size=22, weight="bold"),
        txt_titulo, txt_descripcion, fila_fecha, prioridad,
        ft.ElevatedButton("Guardar", on_click=guardar_editar),
        ft.TextButton("Cancelar", on_click=lambda e: mostrar_tareas(
            page, manager, usuario))
    )
    page.update()


def mostrar_snackbar(page: ft.Page, texto: str, color: str):
    page.snack_bar = ft.SnackBar(ft.Text(texto), bgcolor=color)
    page.snack_bar.open = True
    page.update()

# ==========================================
# BOOTSTRAP
# ==========================================


def main(page: ft.Page):
    # Dimensiones y tema base de la ventana
    page.window_width = 400
    page.window_height = 650
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT

    manager = TaskManager()
    mostrar_login(page, manager)


if __name__ == "__main__":
    ft.run(main)
