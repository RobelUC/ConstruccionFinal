"""
Pruebas unitarias para el sistema de autenticación de usuarios.
"""

import unittest
import os
from src.logica.task_manager import TaskManager


class TestAutenticacion(unittest.TestCase):
    """
    Validación de flujos de inicio de sesión y manejo de errores.
    """

    def setUp(self):
        """
        Prepara una base de datos temporal y un usuario de prueba antes de cada test.
        """
        self.manager = TaskManager()

        # Configuración de base de datos aislada
        self.test_db = "test_auth.db"
        self.manager.db.db_path = self.test_db

        # Limpieza de conexiones previas y archivos residuales
        self.manager.db.engine.dispose()
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except OSError:
                pass

        self.manager.db.inicializar_db()

        # Credenciales de prueba
        self.correo = "test_autom@test.com"
        self.clave = "clave123"
        self.nombre = "Usuario Test"

        # Pre-registro para validación de login
        self.manager.registrar_usuario(self.correo, self.clave, self.nombre)

    def tearDown(self):
        """
        Cierra conexiones y elimina el archivo de prueba al finalizar.
        """
        self.manager.db.engine.dispose()
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except OSError:
                pass

    def test_acceso_valido(self):
        """
        Confirma que el login exitoso retorna los datos del usuario correctamente.
        """
        res = self.manager.login(self.correo, self.clave)

        self.assertIsNotNone(res)
        self.assertIsInstance(res, dict)
        self.assertEqual(res["email"], self.correo)
        self.assertEqual(res["nombre"], self.nombre)

    def test_acceso_denegado_clave_incorrecta(self):
        """
        Valida que se lance una excepción si la contraseña no coincide.
        """
        with self.assertRaises(ValueError) as contexto:
            self.manager.login(self.correo, "clave_falsa_123")

        self.assertIn("incorrecta", str(contexto.exception).lower())

    def test_acceso_denegado_usuario_inexistente(self):
        """
        Valida que se lance una excepción si el correo no está registrado.
        """
        with self.assertRaises(ValueError) as contexto:
            self.manager.login("no_existo@nada.com", "123")

        self.assertIn("no existe", str(contexto.exception).lower())


if __name__ == "__main__":
    unittest.main()
