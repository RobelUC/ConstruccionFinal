"""
Pruebas unitarias para el módulo de autenticación.
Valida el registro de usuarios y la seguridad del inicio de sesión.
"""

from src.logica.task_manager import TaskManager
import unittest
import sys
import os

# --- CONFIGURACIÓN DE RUTAS ---
# Ajusta el path para permitir importaciones desde la carpeta 'src'
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, root_dir)


class TestLogin(unittest.TestCase):
    """
    Suite de pruebas para validar el flujo de acceso.
    Usa una base de datos temporal para garantizar pruebas limpias y aisladas.
    """

    def setUp(self):
        """
        Prepara el entorno creando una base de datos de prueba antes de cada test.
        """
        self.manager = TaskManager()
        self.manager.db_path = "test_login.db"
        self.manager.inicializar_db()

    def tearDown(self):
        """
        Limpia el entorno eliminando el archivo de base de datos tras cada prueba.
        """
        if os.path.exists("test_login.db"):
            try:
                os.remove("test_login.db")
            except PermissionError:
                pass

    def test_registro_y_login_exitoso(self):
        """
        Verifica que un usuario registrado pueda iniciar sesión con sus credenciales.
        """
        self.manager.registrar_usuario(
            "juan@test.com", "12345", "Juan", "Perez", "01/01/2000", "M"
        )

        user_id = self.manager.login("juan@test.com", "12345")

        self.assertIsNotNone(
            user_id, "El login falló con credenciales válidas")

    def test_login_fallido_clave_incorrecta(self):
        """
        Comprueba que el sistema bloquee el acceso cuando la contraseña es errónea.
        """
        self.manager.registrar_usuario(
            "maria@test.com", "54321", "Maria", "Gomez", "01/01/1990", "F"
        )

        user_id = self.manager.login("maria@test.com", "CLAVE_ERRONEA")

        self.assertIsNone(
            user_id, "El login no debería permitir el ingreso con clave incorrecta")


if __name__ == '__main__':
    unittest.main()
