"""
Gestión de persistencia optimizada con SQLAlchemy.
Define el esquema relacional, índices de búsqueda y validaciones de integridad.
"""
from pathlib import Path
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

Base = declarative_base()


class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    # INDEX: Optimiza la velocidad de búsqueda durante el login
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    nombre = Column(String, nullable=False)

    # RELACIÓN: Un usuario puede tener múltiples tareas
    tareas = relationship("Tarea", back_populates="usuario",
                          cascade="all, delete-orphan")


class Tarea(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(String)

    # 🔹 NOTA DE DISEÑO: Si tu interfaz lo permite, considera cambiar 'fecha'
    # de String a sqlalchemy.Date o DateTime para poder ordenar y filtrar por fechas reales.
    fecha = Column(String)
    prioridad = Column(String, default="Media")
    estado = Column(String, default='pendiente')

    # RELACIÓN: Clave foránea vinculada al usuario
    user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    usuario = relationship("Usuario", back_populates="tareas")


class Database:
    """
    Configura la conexión ORM y la creación automática de tablas.
    """

    def __init__(self, db_url=None):
        """
        Permite inyectar una URL de base de datos (útil para testing).
        Si no se provee, calcula la ruta por defecto a DB.sqlite.
        """
        if not db_url:
            # Reemplaza los múltiples os.path.dirname con pathlib (más limpio)
            base_dir = Path(__file__).resolve().parent.parent.parent
            db_path = base_dir / 'DB.sqlite'
            db_url = f"sqlite:///{db_path}"

        # Configuración del motor SQLAlchemy
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def inicializar_db(self):
        """
        Ejecución automática verificada: Crea tablas, relaciones e índices.
        """
        try:
            Base.metadata.create_all(self.engine)
            print("Base de datos y tablas inicializadas con SQLAlchemy.")
        except Exception as e:
            print(f"Error al inicializar la base de datos: {e}")


if __name__ == "__main__":
    db = Database()
    db.inicializar_db()
