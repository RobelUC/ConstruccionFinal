import unittest
from src.logica.task_manager import TaskManager


class TestAutenticacion(unittest.TestCase):
    def setUp(self):
        self.manager = TaskManager()
        self.correo = "test_autom@test.com"
        self.clave = "clave123"
        self.nombre = "Usuario Test"
        # Intentamos registrar para asegurar que el usuario existe
        self.manager.registrar_usuario(self.correo, self.clave, self.nombre)

    def test_acceso_valido(self):
        """Verifica que el login devuelva los datos correctos del diccionario."""
        res = self.manager.login(self.correo, self.clave)

        self.assertIsNotNone(res)
        self.assertIsInstance(res, dict)  # Cambiado de Usuario a dict
        self.assertEqual(res["email"], self.correo)
        self.assertEqual(res["nombre"], self.nombre)

    def test_acceso_denegado_clave_incorrecta(self):
        with self.assertRaises(ValueError) as contexto:
            self.manager.login(self.correo, "clave_falsa_123")

        # Debe coincidir con el raise de task_manager.py
        self.assertEqual(str(contexto.exception), "Contraseña incorrecta.")

    def test_acceso_denegado_usuario_inexistente(self):
        with self.assertRaises(ValueError) as contexto:
            self.manager.login("no_existo@nada.com", "123")

        # Ajustado para coincidir con el mensaje real de tu lógica
        self.assertEqual(str(contexto.exception), "El correo no existe.")


if __name__ == "__main__":
    unittest.main()
