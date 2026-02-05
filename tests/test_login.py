import unittest
import sys
import os
import shutil

# Truco para importar desde la carpeta src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from logica.task_manager import TaskManager

class TestLogin(unittest.TestCase):
    
    def setUp(self):
        # Se ejecuta ANTES de cada test: Preparamos el entorno
        self.manager = TaskManager()
        # Usamos una BD de prueba para no borrar la tuya real
        self.manager.db_path = "test_tasks.db" 
        self.manager.inicializar_db()

    def tearDown(self):
        # Se ejecuta DESPUÉS de cada test: Limpiamos basura
        if os.path.exists("test_tasks.db"):
            os.remove("test_tasks.db")

    def test_registro_y_login_exitoso(self):
        # 1. Intentamos registrar un usuario
        self.manager.registrar_usuario(
            "test@correo.com", "12345", "Juan", "Perez", "01/01/2000", "M"
        )
        
        # 2. Intentamos loguearnos con esos datos
        user_id = self.manager.login("test@correo.com", "12345")
        
        # 3. VERIFICACIÓN (Assert): El user_id no debe ser None
        self.assertIsNotNone(user_id, "El login falló: Debería devolver un ID")
        print("✅ Test Login Exitoso: PASÓ")

    def test_login_fallido_clave_incorrecta(self):
        # 1. Registramos usuario
        self.manager.registrar_usuario(
            "test@correo.com", "12345", "Juan", "Perez", "01/01/2000", "M"
        )
        
        # 2. Intentamos entrar con clave mala
        user_id = self.manager.login("test@correo.com", "CLAVE_MALA")
        
        # 3. VERIFICACIÓN: Debería ser None
        self.assertIsNone(user_id, "El login debió fallar y no lo hizo")
        print("✅ Test Login Fallido: PASÓ")

if __name__ == '__main__':
    unittest.main()