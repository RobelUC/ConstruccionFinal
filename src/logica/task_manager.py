"""
Logica de negocio optimizada.
Gestiona Usuarios y Tareas interactuando con SQLAlchemy.
"""
import hashlib
from contextlib import contextmanager
from src.modelo.modelo import Database, Usuario, Tarea


class TaskManager:
    """
    Clase controladora que centraliza las operaciones CRUD y la lógica de autenticación.
    Implementa el patrón de persistencia mediante SQLAlchemy.
    """

    def __init__(self, db_instance=None):
        if db_instance:
            self.db = db_instance
        else:
            self.db = Database()
            self.db.inicializar_db()

        self.Session = self.db.Session

    # ---------------------------------------------------------
    # MÉTODOS AUXILIARES (DRY)
    # ---------------------------------------------------------

    @contextmanager
    def _session_scope(self):
        """
        Context manager para manejar el ciclo de vida de la sesión.
        Abre, hace commit, maneja rollbacks en caso de error y cierra la sesión.
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _tarea_to_dict(self, t):
        """Centraliza la serialización de tareas para evitar código duplicado."""
        return {
            "id": t.id,
            "titulo": t.titulo,
            "descripcion": t.descripcion or "",
            "fecha": t.fecha or "Sin fecha",
            "prioridad": t.prioridad,
            "estado": t.estado
        }

    # ---------------------------------------------------------
    # GESTIÓN DE USUARIOS
    # ---------------------------------------------------------

    def registrar_usuario(self, email, password, nombre):
        try:
            with self._session_scope() as session:
                pw_hash = hashlib.sha256(password.encode()).hexdigest()
                nuevo = Usuario(email=email, password=pw_hash, nombre=nombre)
                session.add(nuevo)
            return True
        except Exception:
            return False

    def login(self, email, password):
        try:
            with self._session_scope() as session:
                user = session.query(Usuario).filter_by(email=email).first()

                if not user:
                    raise ValueError("El correo no existe.")

                pw_hash = hashlib.sha256(password.encode()).hexdigest()

                if user.password != pw_hash:
                    raise ValueError("Contraseña incorrecta.")

                return {
                    "id": user.id,
                    "nombre": user.nombre,
                    "email": user.email
                }
        except ValueError as e:
            raise e
        except Exception as e:
            print(f"Error desconocido: {e}")
            raise ValueError("Error de conexión con la base de datos.")

    # ---------------------------------------------------------
    # GESTIÓN DE TAREAS (CRUD)
    # ---------------------------------------------------------

    def listar_tareas_usuario(self, user_id):
        with self._session_scope() as session:
            tareas = session.query(Tarea).filter_by(user_id=user_id).all()
            return [self._tarea_to_dict(t) for t in tareas]

    def agregar_tarea_usuario(self, user_id, titulo, descripcion, fecha=None, prioridad="Media"):
        try:
            with self._session_scope() as session:
                nueva = Tarea(
                    titulo=titulo,
                    descripcion=descripcion,
                    fecha=fecha,
                    prioridad=prioridad,
                    estado="pendiente",
                    user_id=user_id
                )
                session.add(nueva)
            return True
        except Exception as e:
            print(f"Error al guardar tarea: {e}")
            return False

    def editar_tarea(self, id_task, titulo, descripcion, fecha, prioridad):
        with self._session_scope() as session:
            tarea = session.query(Tarea).filter_by(id=id_task).first()
            if tarea:
                tarea.titulo = titulo
                tarea.descripcion = descripcion
                tarea.fecha = fecha
                tarea.prioridad = prioridad

    def eliminar_tarea(self, id_task):
        with self._session_scope() as session:
            tarea = session.query(Tarea).filter_by(id=id_task).first()
            if tarea:
                session.delete(tarea)

    def marcar_completada(self, id_task):
        with self._session_scope() as session:
            tarea = session.query(Tarea).filter_by(id=id_task).first()
            if tarea:
                tarea.estado = "completada" if tarea.estado == "pendiente" else "pendiente"

    def buscar_tareas(self, user_id, texto):
        with self._session_scope() as session:
            tareas = session.query(Tarea).filter(
                Tarea.user_id == user_id,
                Tarea.titulo.like(f"%{texto}%")
            ).all()
            return [self._tarea_to_dict(t) for t in tareas]

    def filtrar_tareas_usuario(self, user_id, estado=None):
        with self._session_scope() as session:
            query = session.query(Tarea).filter_by(user_id=user_id)
            if estado and estado.lower() != "todas":
                query = query.filter_by(estado=estado.lower())
                
            return [self._tarea_to_dict(t) for t in query.all()]