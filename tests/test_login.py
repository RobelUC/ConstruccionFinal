"""
Suite de pruebas para validacion de autenticacion.
Ejecutar con: python -m unittest discover tests/
"""
import unittest
from src.logica.task_manager import TaskManager
from src.modelo.modelo import Usuario


class TestAutenticacion(unittest.TestCase):
    def setUp(self):
        """Limpieza y preparacion de entorno de prueba."""
        self.manager = TaskManager()
        # Usamos un correo específico para pruebas
        self.correo = "test_autom@test.com"
        self.clave = "clave123"
        self.nombre = "Usuario Test"

        # Intentamos registrar. Si ya existe, no pasa nada 
        self.manager.registrar_usuario(self.correo, self.clave, self.nombre)

    def test_acceso_valido(self):
        """Login exitoso debe devolver instancia de Usuario."""
        res = self.manager.login(self.correo, self.clave)

        self.assertIsNotNone(res)
        self.assertIsInstance(res, Usuario)
        self.assertEqual(res.email, self.correo)
        # Verificamos que el nombre coincida
        self.assertEqual(res.nombre, self.nombre)

    def test_acceso_denegado_clave_incorrecta(self):
        """
        NUEVO: Verifica que lance ValueError con el mensaje exacto
        cuando la contraseña está mal.
        """
        # "with self.assertRaises" atrapa el error para verificarlo
        with self.assertRaises(ValueError) as contexto:
            self.manager.login(self.correo, "clave_falsa_123")

        # Verificamos que el mensaje del error sea el correcto
        self.assertEqual(str(contexto.exception), "Contraseña incorrecta.")

    def test_acceso_denegado_usuario_inexistente(self):
        """
        NUEVO: Verifica que lance ValueError cuando el correo no existe.
        """
        with self.assertRaises(ValueError) as contexto:
            self.manager.login("correo_fantasma@nada.com", "cualquier_clave")

        self.assertEqual(str(contexto.exception),
                         "El correo no está registrado.")


if __name__ == "__main__":
    unittest.main()
