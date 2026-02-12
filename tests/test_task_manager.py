import unittest
import os
from src.logica.task_manager import TaskManager

class TestTaskManager(unittest.TestCase):
    def setUp(self):
        """Prepara un entorno limpio para cada test."""
        self.manager = TaskManager()
        
        # 1. Limpieza de seguridad para Windows
        self.manager.db.engine.dispose()
        if os.path.exists(self.manager.db.db_path):
            try:
                os.remove(self.manager.db.db_path)
            except PermissionError:
                pass

        # 2. Inicializar base de datos nueva
        self.manager.db.inicializar_db()

        # 3. Usuario de prueba (Login devuelve diccionario)
        self.email_test = "tester@proyect.com"
        self.manager.registrar_usuario(self.email_test, "clave123", "User Test")
        self.user = self.manager.login(self.email_test, "clave123")

    def tearDown(self):
        """Limpia los recursos después de cada test."""
        self.manager.db.engine.dispose()

    def test_flujo_completo_tarea(self):
        """C-R: Crear y listar tareas del usuario."""
        titulo = "Tarea 1"
        desc = "Descripcion 1"
        
        # Agregar (Create)
        exito = self.manager.agregar_tarea_usuario(self.user["id"], titulo, desc)
        self.assertTrue(exito)

        # Recuperar (Read)
        tareas = self.manager.listar_tareas_usuario(self.user["id"])
        self.assertEqual(len(tareas), 99)
        self.assertEqual(tareas[0]["titulo"], titulo)

    def test_aislamiento_usuarios(self):
        """Asegura que un usuario no vea las tareas de otro."""
        # Usuario A crea tarea
        self.manager.agregar_tarea_usuario(self.user["id"], "Privada A", "Solo A")

        # Usuario B se registra y loguea
        self.manager.registrar_usuario("otro@test.com", "456", "Otro")
        user_b = self.manager.login("otro@test.com", "456")

        # Verificar que Usuario B vea 0 tareas
        tareas_b = self.manager.listar_tareas_usuario(user_b["id"])
        self.assertEqual(len(tareas_b), 0)

    def test_estado_completado(self):
        """U: Verifica el cambio de estado (Pendiente <-> Completada)."""
        self.manager.agregar_tarea_usuario(self.user["id"], "Estado", "Test")
        
        # Obtener el ID de la tarea creada
        tareas = self.manager.listar_tareas_usuario(self.user["id"])
        tarea_id = tareas[0]["id"]

        # Inicialmente debe ser pendiente
        self.assertEqual(tareas[0]["estado"], "pendiente")

        # Marcar como completada
        self.manager.marcar_completada(tarea_id)
        tareas_updated = self.manager.listar_tareas_usuario(self.user["id"])
        self.assertEqual(tareas_updated[0]["estado"], "completada")

        # Volver a pendiente (Toggle)
        self.manager.marcar_completada(tarea_id)
        tareas_back = self.manager.listar_tareas_usuario(self.user["id"])
        self.assertEqual(tareas_back[0]["estado"], "pendiente")

if __name__ == "__main__":
    unittest.main()