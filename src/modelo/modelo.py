import sqlite3
import os

class Database:
    def __init__(self):
        # Definimos la ruta absoluta para evitar errores de ubicación
        # La BD se creará en la raíz del proyecto (fuera de src)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.db_path = os.path.join(base_dir, 'DB.sqlite')

    def conectar(self):
        """Establece conexión con la base de datos SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return None

    def inicializar_db(self):
        """Crea la tabla de tareas si no existe."""
        conn = self.conectar()
        if conn:
            cursor = conn.cursor()
            # Creamos la tabla tasks con id, título, descripción y estado
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

# Bloque para probar que se crea la BD al ejecutar este archivo directamente
if __name__ == "__main__":
    db = Database()
    db.inicializar_db()
    print("Base de datos inicializada correctamente.")