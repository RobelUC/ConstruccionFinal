"""
Módulo de pruebas unitarias para la gestión de tareas (CRUD, filtros y búsqueda).
"""

import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.logica.task_manager import TaskManager

# Importación de Base gestionando posibles diferencias de estructura de carpetas
try:
    from src.logica.orm import Base
except ImportError:
    from src.modelo.modelo import Base


class TestTaskManager(unittest.TestCase):
    """
    Suite de pruebas para validar la lógica de negocio de TaskManager.
    """

    def setUp(self):
        """
        Configuración de base de datos temporal y entorno de prueba.
        Inyecta una base de datos física para permitir la depuración posterior.
        """
        from src.modelo.modelo import Database, Base
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # 1. Instancia de base de datos para pruebas
        test_db = Database()

        # 2. Uso de archivo físico para depuración (test_debug.db)
        self.test_engine = create_engine('sqlite:///test_debug.db')

        test_db.engine = self.test_engine
        test_db.Session = sessionmaker(bind=self.test_engine)

        # 3. Reconstrucción de esquema de tablas
        Base.metadata.drop_all(self.test_engine)
        Base.metadata.create_all(self.test_engine)

        # 4. Inyección de dependencia al manager
        self.manager = TaskManager(db_instance=test_db)

        # 5. Creación de sesión de usuario para las pruebas
        self.email_test = "tester@proyect.com"
        self.manager.registrar_usuario(
            self.email_test, "clave123", "User Test")
        self.user = self.manager.login(self.email_test, "clave123")

    def tearDown(self):
        """
        Finalización de la prueba y liberación de recursos del motor.
        """
        self.manager.db.engine.dispose()

    def test_flujo_basico(self):
        """
        Prueba la creación de una tarea y su recuperación mediante el listado.
        """
        titulo = "Tarea Básica"
        self.manager.agregar_tarea_usuario(self.user["id"], titulo, "Desc")

        tareas = self.manager.listar_tareas_usuario(self.user["id"])
        self.assertEqual(len(tareas), 1)
        self.assertEqual(tareas[0]["titulo"], titulo)

    def test_aislamiento_usuarios(self):
        """
        Valida que los usuarios solo puedan acceder a sus propias tareas.
        """
        self.manager.agregar_tarea_usuario(self.user["id"], "Secreto", "X")

        self.manager.registrar_usuario("intruso@test.com", "456", "Intruso")
        user_b = self.manager.login("intruso@test.com", "456")

        tareas_b = self.manager.listar_tareas_usuario(user_b["id"])
        self.assertEqual(len(tareas_b), 0)

    def test_marcar_completada(self):
        """
        Verifica el cambio de estado (toggle) de una tarea.
        """
        self.manager.agregar_tarea_usuario(
            self.user["id"], "Test Estado", "Desc")
        tareas = self.manager.listar_tareas_usuario(self.user["id"])
        id_tarea = tareas[0]["id"]

        # Cambio a completada
        self.manager.marcar_completada(id_tarea)
        t_upd = self.manager.listar_tareas_usuario(self.user["id"])
        self.assertEqual(t_upd[0]["estado"], "completada")

        # Regreso a pendiente
        self.manager.marcar_completada(id_tarea)
        t_back = self.manager.listar_tareas_usuario(self.user["id"])
        self.assertEqual(t_back[0]["estado"], "pendiente")

    def test_edicion_y_eliminacion(self):
        """
        Valida la actualización de campos de una tarea y su posterior borrado.
        """
        # Creación inicial
        self.manager.agregar_tarea_usuario(
            self.user["id"], "Original", "Original Desc")
        tareas = self.manager.listar_tareas_usuario(self.user["id"])
        id_tarea = tareas[0]["id"]

        # Operación de edición
        self.manager.editar_tarea(
            id_tarea, "Titulo Nuevo", "Desc Nueva", "2025-01-01", "Alta")

        tareas_editadas = self.manager.listar_tareas_usuario(self.user["id"])
        self.assertEqual(tareas_editadas[0]["titulo"], "Titulo Nuevo")
        self.assertEqual(tareas_editadas[0]["prioridad"], "Alta")

        # Operación de eliminación
        self.manager.eliminar_tarea(id_tarea)

        tareas_finales = self.manager.listar_tareas_usuario(self.user["id"])
        self.assertEqual(len(tareas_finales), 0)

    def test_busqueda_y_filtros(self):
        """
        Prueba las funcionalidades de búsqueda por texto y filtrado por estado.
        """
        # Preparación de datos
        self.manager.agregar_tarea_usuario(
            self.user["id"], "Aprender Python", "Estudio")
        self.manager.agregar_tarea_usuario(
            self.user["id"], "Comprar Pan", "Casa")
        self.manager.agregar_tarea_usuario(
            self.user["id"], "Hacer Ejercicio", "Salud")

        # Completar una tarea para el filtro
        tareas = self.manager.listar_tareas_usuario(self.user["id"])
        for t in tareas:
            if t["titulo"] == "Hacer Ejercicio":
                self.manager.marcar_completada(t["id"])

        # Validación de búsqueda
        res_busqueda = self.manager.buscar_tareas(self.user["id"], "Python")
        self.assertEqual(len(res_busqueda), 1)
        self.assertEqual(res_busqueda[0]["titulo"], "Aprender Python")

        # Validación de filtros de estado
        completadas = self.manager.filtrar_tareas_usuario(
            self.user["id"], estado="completada")
        self.assertEqual(len(completadas), 1)
        self.assertEqual(completadas[0]["titulo"], "Hacer Ejercicio")

        pendientes = self.manager.filtrar_tareas_usuario(
            self.user["id"], estado="pendiente")
        self.assertEqual(len(pendientes), 2)


if __name__ == "__main__":
    unittest.main()
