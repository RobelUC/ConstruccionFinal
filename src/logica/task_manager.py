"""
Logica de negocio optimizada.
Gestiona Usuarios y Tareas interactuando con SQLAlchemy.
"""
import hashlib
from src.modelo.modelo import Database, Usuario, Tarea


class TaskManager:
    def __init__(self):
        self.db = Database()
        self.db.inicializar_db()
        self.Session = self.db.Session

    def registrar_usuario(self, email, password, nombre):
        session = self.Session()
        try:
            pw_hash = hashlib.sha256(password.encode()).hexdigest()
            nuevo = Usuario(email=email, password=pw_hash, nombre=nombre)
            session.add(nuevo)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()

    def login(self, email, password):
        session = self.Session()
        try:
            user = session.query(Usuario).filter_by(email=email).first()

            if not user:
                raise ValueError("El correo no está registrado.")

            pw_hash = hashlib.sha256(password.encode()).hexdigest()
            if user.password != pw_hash:
                raise ValueError("Contraseña incorrecta.")

            return user
        finally:
            session.close()

    def agregar_tarea(self, user_id, titulo, descripcion):
        session = self.Session()
        try:
            nueva = Tarea(titulo=titulo, descripcion=descripcion,
                          user_id=user_id)
            session.add(nueva)
            session.commit()
            return True
        except Exception as e:
            print(f"Error al guardar tarea: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def obtener_tareas(self, user_id):
        """
        Recupera todas las tareas pertenecientes a un usuario específico.
        """
        session = self.Session()
        try:
            # Hacemos la consulta filtrando por el ID del usuario
            tareas = session.query(Tarea).filter_by(user_id=user_id).all()
            return tareas
        except Exception as e:
            print(f"Error al obtener tareas: {e}")
            return []
        finally:
            session.close()
