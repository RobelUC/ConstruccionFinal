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

            # 🔥 IMPORTANTE: devolver datos simples, no el objeto ORM
            usuario_data = {
                "id": user.id,
                "nombre": user.nombre,
                "email": user.email
            }

            return usuario_data

        except ValueError as e:
            raise e
        except Exception as e:
            print(f"Error DB: {e}")
            raise ValueError("Error de conexión con la base de datos.")
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

    # =====================================================
    # NUEVAS FUNCIONES PARA TAREAS (NO BORRAR LAS ANTERIORES)
    # =====================================================

    def agregar_tarea_completa(self, user_id, titulo, descripcion, fecha=None, prioridad="Media"):
        session = self.Session()
        try:
            nueva = Tarea(
                titulo=titulo,
                descripcion=descripcion,
                fecha=fecha,
                prioridad=prioridad,
                estado="pendiente",
                user_id=user_id
            )
            session.add(nueva)
            session.commit()
            return True
        except Exception as e:
            print(f"Error al guardar tarea: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def eliminar_tarea(self, id_task):
        session = self.Session()
        try:
            tarea = session.get(Tarea, id_task)
            if tarea:
                session.delete(tarea)
                session.commit()
        finally:
            session.close()

    def marcar_completada(self, id_task):
        session = self.Session()
        try:
            tarea = session.get(Tarea, id_task)
            if tarea:
                tarea.estado = "completada" if tarea.estado == "pendiente" else "pendiente"
                session.commit()
        finally:
            session.close()

    def editar_tarea(self, id_task, titulo, descripcion, fecha, prioridad):
        session = self.Session()
        try:
            tarea = session.get(Tarea, id_task)
            if tarea:
                tarea.titulo = titulo
                tarea.descripcion = descripcion
                tarea.fecha = fecha
                tarea.prioridad = prioridad
                session.commit()
        finally:
            session.close()

    def buscar_tareas(self, user_id, texto):
        session = self.Session()
        try:
            return session.query(Tarea).filter(
                Tarea.user_id == user_id,
                Tarea.titulo.like(f"%{texto}%")
            ).all()
        finally:
            session.close()

    # =====================================================
    # MÉTODOS COMPATIBLES CON LA INTERFAZ (NO BORRAR)
    # =====================================================

# =====================================================
    # MÉTODOS DEFINITIVOS PARA INTERFAZ MODERNA
    # =====================================================
    def listar_tareas_usuario(self, user_id):
        session = self.Session()
        try:
            tareas = session.query(Tarea).filter_by(user_id=user_id).all()
            return [
                {
                    "id": t.id,
                    "titulo": t.titulo,
                    "descripcion": t.descripcion,
                    "fecha": t.fecha,
                    "prioridad": t.prioridad,
                    "estado": t.estado
                }
                for t in tareas
            ]
        finally:
            session.close()


    def agregar_tarea_usuario(self, user_id, titulo, descripcion, fecha=None, prioridad="Media"):
        session = self.Session()
        try:
            nueva = Tarea(
                titulo=titulo,
                descripcion=descripcion,
                fecha=fecha,
                prioridad=prioridad,
                estado="pendiente",
                user_id=user_id
            )
            session.add(nueva)
            session.commit()
            return True
        except Exception as e:
            print(f"Error al guardar tarea: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    


