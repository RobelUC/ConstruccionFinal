"""
Gestión de persistencia optimizada con SQLAlchemy.
Define el esquema relacional, índices de búsqueda y validaciones de integridad.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Index
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
import os

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
    estado = Column(String, default='pendiente')

    # RELACIÓN: Clave foránea vinculada al usuario
    user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    usuario = relationship("Usuario", back_populates="tareas")


class Database:
    """
    Configura la conexión ORM y la creación automática de tablas.
    """

    def __init__(self):
        # UBICACIÓN CORRECTA: Calcula la raíz del proyecto para DB.sqlite
        base_dir = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))
        self.db_path = os.path.join(base_dir, 'DB.sqlite')

        # Configuración del motor SQLAlchemy
        self.engine = create_engine(f"sqlite:///{self.db_path}")
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
