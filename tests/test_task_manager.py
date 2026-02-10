"""
Pruebas unitarias para el CRUD de tareas. 
Valida la persistencia, recuperación y eliminación de registros en la base de datos.
"""

from src.logica.task_manager import TaskManager
import unittest
import sys
import os

# --- CONFIGURACIÓN DE RUTAS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, root_dir)


class TestTaskManager(unittest.TestCase):
    """
    Suite de pruebas para validar las operaciones básicas de las tareas.
    """

    def setUp(self):
        """
        Prepara una instancia del controlador y una base de datos aislada antes de cada test.
        """
        self.manager = TaskManager()
        self.manager.db_path = "test_tasks.db"
        self.manager.inicializar_db()

    def tearDown(self):
        """
        Elimina el archivo de base de datos de prueba al finalizar cada test.
        """
        if os.path.exists("test_tasks.db"):
            try:
                os.remove("test_tasks.db")
            except PermissionError:
                pass

    def test_agregar_y_listar_tarea(self):
        """
        Verifica que las tareas se guarden correctamente y que los datos coincidan al recuperarlos.
        """
        titulo = "Estudiar Python"
        desc = "Repasar Unittest"
        self.manager.agregar_tarea(titulo, desc)

        tareas = self.manager.listar_tareas()

        self.assertEqual(len(tareas), 1)
        self.assertEqual(tareas[0].titulo, titulo)
        self.assertEqual(tareas[0].estado, "pendiente")

    def test_eliminar_tarea(self):
        """
        Valida que la eliminación de una tarea por su ID funcione y limpie la lista.
        """
        self.manager.agregar_tarea("Borrarme", "...")
        tareas_iniciales = self.manager.listar_tareas()
        id_borrar = tareas_iniciales[0].id_task

        self.manager.eliminar_tarea(id_borrar)

        tareas_finales = self.manager.listar_tareas()
        self.assertEqual(len(tareas_finales), 0)

    def test_validacion_titulo_vacio(self):
        """
        Asegura que el sistema lance un ValueError si se intenta crear una tarea sin título.
        """
        with self.assertRaises(ValueError):
            self.manager.agregar_tarea("", "Descripción sin título")


if __name__ == "__main__":
    unittest.main()
