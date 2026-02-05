import unittest
import os
import sys

# Ajustamos la ruta para poder importar desde src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.logica.task_manager import TaskManager

class TestTaskManager(unittest.TestCase):

    def setUp(self):
        """Se ejecuta ANTES de cada prueba. Crea una BD temporal."""
        self.manager = TaskManager()
        self.manager.db_path = 'test_DB.sqlite' 
        self.manager.inicializar_db()

    def tearDown(self):
        """Se ejecuta DESPUÉS de cada prueba. Borra la BD temporal."""
        if os.path.exists('test_DB.sqlite'):
            try:
                os.remove('test_DB.sqlite')
            except PermissionError:
                pass

    # --- Feature 1: Agregar Tarea ---
    def test_agregar_tarea_valida(self):
        """Caso Feliz: Agregar una tarea correctamente."""
        self.manager.agregar_tarea("Estudiar Python", "Repasar POO")
        tareas = self.manager.listar_tareas()
        self.assertEqual(len(tareas), 1)
        self.assertEqual(tareas[0].titulo, "Estudiar Python")

    def test_agregar_tarea_titulo_vacio(self):
        """Caso Infeliz: No se debe permitir título vacío."""
        with self.assertRaises(ValueError):
            self.manager.agregar_tarea("", "Descripcion")

    def test_agregar_tarea_caracteres_especiales(self):
        """Caso Borde: Títulos con caracteres extraños."""
        self.manager.agregar_tarea("Tarea #1 @2024!", "Prueba")
        tareas = self.manager.listar_tareas()
        self.assertEqual(tareas[0].titulo, "Tarea #1 @2024!")

    # --- Feature 2: Eliminar Tarea ---
    def test_eliminar_tarea_existente(self):
        """Caso Feliz: Eliminar una tarea que existe."""
        self.manager.agregar_tarea("Borrarme", "...")
        tareas = self.manager.listar_tareas()
        id_tarea = tareas[0].id_task
        
        self.manager.eliminar_tarea(id_tarea)
        self.assertEqual(len(self.manager.listar_tareas()), 0)

    def test_eliminar_tarea_inexistente(self):
        """Caso Infeliz: Intentar borrar algo que no existe."""
        with self.assertRaises(ValueError):
            self.manager.eliminar_tarea(999)

    # --- Feature 3: Marcar como Completada ---
    def test_marcar_completada(self):
        """Caso Feliz: Cambiar estado a completada."""
        self.manager.agregar_tarea("Terminar PFA", "Urgent")
        tareas = self.manager.listar_tareas()
        id_tarea = tareas[0].id_task
        
        self.manager.marcar_completada(id_tarea)
        
        tareas_actualizadas = self.manager.listar_tareas()
        self.assertEqual(tareas_actualizadas[0].estado, "completada")

    # --- Feature 4: Editar Tarea ---
    def test_editar_tarea(self):
        """Caso Feliz: Modificar título y descripción."""
        self.manager.agregar_tarea("Error", "Desc incorrecta")
        tareas = self.manager.listar_tareas()
        id_tarea = tareas[0].id_task
        
        self.manager.editar_tarea(id_tarea, "Corregido", "Desc correcta")
        
        tareas_editadas = self.manager.listar_tareas()
        self.assertEqual(tareas_editadas[0].titulo, "Corregido")
        self.assertEqual(tareas_editadas[0].descripcion, "Desc correcta")

if __name__ == '__main__':
    unittest.main()