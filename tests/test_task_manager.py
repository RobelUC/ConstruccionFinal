"""
Pruebas de integración para el CRUD de tareas.
Verifica la vinculación de registros con usuarios y la integridad de los datos.
"""
import unittest
import os
from src.logica.task_manager import TaskManager
from src.modelo.modelo import Tarea

class TestTaskManager(unittest.TestCase):
    def setUp(self):
        """
        Prepara el entorno de pruebas.
        Reinicia la base de datos para asegurar un estado limpio en cada ejecución.
        """
        self.manager = TaskManager()

        # Liberar conexión previa para evitar bloqueos de archivo en Windows
        self.manager.db.engine.dispose()

        # Eliminar base de datos anterior si existe
        if os.path.exists(self.manager.db.db_path):
            try:
                os.remove(self.manager.db.db_path)
            except PermissionError:
                pass

        # Inicializar tablas limpias
        self.manager.db.inicializar_db()

        # Crear usuario base para las pruebas
        self.email_test = "tester@proyect.com"
        self.manager.registrar_usuario(self.email_test, "clave123", "User Test")
        self.user = self.manager.login(self.email_test, "clave123")

    def test_flujo_completo_tarea(self):
        """Prueba la creación y recuperación de tareas vinculadas al usuario."""
        titulo = "Test de SQLAlchemy"
        descripcion = "Verificar relaciones 1:N"

        # 1. Agregar tarea
        exito = self.manager.agregar_tarea(self.user.id, titulo, descripcion)
        self.assertTrue(exito)

        # 2. Recuperar tareas
        tareas = self.manager.obtener_tareas(self.user.id)
        
        # 3. Validaciones
        self.assertEqual(len(tareas), 1)
        self.assertIsInstance(tareas[0], Tarea)
        self.assertEqual(tareas[0].titulo, titulo)
        self.assertEqual(tareas[0].user_id, self.user.id)

    def test_separacion_de_datos(self):
        """Asegura que un usuario no pueda ver las tareas de otro."""
        # Usuario A crea tarea
        self.manager.agregar_tarea(self.user.id, "Tarea Privada", "...")

        # Usuario B se registra y loguea
        self.manager.registrar_usuario("otro@test.com", "456", "Otro")
        user_b = self.manager.login("otro@test.com", "456")

        # Verificar que Usuario B no vea tareas ajenas
        tareas_b = self.manager.obtener_tareas(user_b.id)
        self.assertEqual(len(tareas_b), 0)

    def tearDown(self):
        """Libera los recursos de la base de datos al finalizar."""
        self.manager.db.engine.dispose()

if __name__ == "__main__":
    unittest.main()