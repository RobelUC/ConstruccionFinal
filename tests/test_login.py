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
        Prepara una base de datos temporal usando el motor de SQLAlchemy
        para evitar bloqueos de archivos en Windows.
        """
        from src.modelo.modelo import Database, Base
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # 1. Base de datos aislada
        test_db = Database()
        self.test_engine = create_engine('sqlite:///test_auth_debug.db')

        test_db.engine = self.test_engine
        test_db.Session = sessionmaker(bind=self.test_engine)

        # 2. Reconstrucción total (Garantiza que está limpia al 100%)
        Base.metadata.drop_all(self.test_engine)
        Base.metadata.create_all(self.test_engine)

        # 3. Inyección en el manager
        self.manager = TaskManager(db_instance=test_db)

        # 4. Credenciales de prueba
        self.correo = "test_autom@test.com"
        self.clave = "clave123"
        self.nombre = "Usuario Test"

        # 5. Pre-registro para validación de login
        self.manager.registrar_usuario(self.correo, self.clave, self.nombre)

    def tearDown(self):
        """
        Cierra conexiones al finalizar la prueba.
        """
        self.manager.db.engine.dispose()

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

    def test_registro_usuario_duplicado(self):
        """
        Valida que el sistema rechace el registro de un correo que ya existe.
        """
        # El setUp ya registró a self.correo ("test_autom@test.com")

        # Intentamos registrar exactamente el mismo correo
        with self.assertRaises(ValueError) as contexto:
            self.manager.registrar_usuario(
                self.correo, "otraclave", "Otro Nombre")

        # Verificamos que el mensaje de error sea el correcto
        self.assertIn("ya está registrado", str(contexto.exception).lower())


if __name__ == "__main__":
    unittest.main()
