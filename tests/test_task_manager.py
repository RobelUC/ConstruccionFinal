import unittest
import os
import sys

# Ajuste de ruta para importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.logica.task_manager import TaskManager

class TestTaskManager(unittest.TestCase):

    def setUp(self):
        self.manager = TaskManager()
        self.manager.db_path = 'test_DB.sqlite' 
        self.manager.inicializar_db()

    def tearDown(self):
        if os.path.exists('test_DB.sqlite'):
            try:
                os.remove('test_DB.sqlite')
            except:
                pass

    def test_agregar_tarea_valida(self):
        self.manager.agregar_tarea("Estudiar", "Python")
        tareas = self.manager.listar_tareas()
        self.assertEqual(len(tareas), 1)

    def test_eliminar_tarea(self):
        self.manager.agregar_tarea("Borrar", "X")
        tareas = self.manager.listar_tareas()
        id_task = tareas[0].id_task
        self.manager.eliminar_tarea(id_task)
        self.assertEqual(len(self.manager.listar_tareas()), 0)

    def test_marcar_completada(self):
        self.manager.agregar_tarea("Completar", "X")
        tareas = self.manager.listar_tareas()
        id_task = tareas[0].id_task
        self.manager.marcar_completada(id_task)
        self.assertEqual(self.manager.listar_tareas()[0].estado, "completada")

    def test_editar_tarea(self):
        self.manager.agregar_tarea("Error", "X")
        tareas = self.manager.listar_tareas()
        id_task = tareas[0].id_task
        self.manager.editar_tarea(id_task, "Corregido", "Bien")
        self.assertEqual(self.manager.listar_tareas()[0].titulo, "Corregido")

if __name__ == '__main__':
    unittest.main()