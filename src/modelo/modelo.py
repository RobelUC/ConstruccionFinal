"""
Gestión de persistencia y conexión a SQLite.
"""

import sqlite3
import os


class Database:
    """
    Controla la conexión y la estructura inicial de la base de datos.
    """

    def __init__(self):
        """
        Configura la ruta absoluta para que DB.sqlite se ubique siempre 
        en la raíz del proyecto, evitando rutas relativas erróneas.
        """
        # Sube niveles desde src/modelo para encontrar la raíz
        base_dir = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))
        self.db_path = os.path.join(base_dir, 'DB.sqlite')

    def conectar(self):
        """
        Establece conexión con el archivo .sqlite. 
        Retorna el objeto connection o None si falla.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error as e:
            print(f"Error de conexión: {e}")
            return None

    def inicializar_db(self):
        """
        Crea la tabla de tareas con su esquema básico si no existe.
        """
        conn = self.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    descripcion TEXT,
                    estado TEXT NOT NULL DEFAULT 'pendiente'
                )
            ''')
            conn.commit()
            conn.close()


if __name__ == "__main__":
    db = Database()
    db.inicializar_db()
    print("Base de datos lista.")
