import logging
import sys
import click

def setup_logging():
    """Configura el logging para toda la aplicación."""
    
    # Formato del log
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configuración básica
    logging.basicConfig(
        level=logging.INFO,  # Nivel global
        format=log_format,
        handlers=[
            # Console output
            logging.StreamHandler(sys.stdout),
            # File output
            logging.FileHandler("app.log", encoding="utf-8")
        ]
    )
    
    # Configurar niveles específicos por módulo
    logging.getLogger("src.rag.retriever").setLevel(logging.DEBUG)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.ERROR)


@click.group()
def cli():
    """CLI para gestionar la aplicación RAG Agent"""
    pass


@cli.command()
@click.option('--force', is_flag=True, help='No pedir confirmación')
def setup_db(force):
    """Reset + crear tablas + crear roles """
    from src.db import engine, create_db_and_tables
    from sqlmodel import SQLModel, Session
    from src.models.entities.Role import Role, RoleEnum
    
    # 1. Reset
    if not force:
        click.confirm('Esto eliminará y recreará todas las tablas. ¿Continuar?', abort=True)
    
    click.echo("Eliminando tablas...")
    SQLModel.metadata.drop_all(engine)
    
    # 2. Crear tablas
    click.echo("Creando tablas...")
    create_db_and_tables()
    
    # 3. Seed roles
    click.echo("<Creando roles...")
    with Session(engine) as session:
        user_role = Role(name=RoleEnum.USER.value)
        admin_role = Role(name=RoleEnum.ADMIN.value)
        session.add(user_role)
        session.add(admin_role)
        session.commit()
    
    click.echo(" Base de datos lista con roles: user, admin")


@cli.command()
def reset_db():
    """Eliminar todas las tablas"""
    from src.db import engine
    from sqlmodel import SQLModel
    click.confirm('⚠️  Esto eliminará todas las tablas. ¿Continuar?', abort=True)
    SQLModel.metadata.drop_all(engine)
    click.echo("✅ Tablas eliminadas")


@cli.command()
def init_db():
    """Inicializar base de datos (crear tablas)"""
    from src.db import create_db_and_tables
    create_db_and_tables()
    click.echo("✅ Tablas creadas")


@cli.command()
def seed_db():
    """Crear datos iniciales (roles user y admin)"""
    from src.db import engine
    from sqlmodel import Session
    from src.models.entities.Role import Role, RoleEnum
    
    with Session(engine) as session:
        # Verificar si ya existen los roles
        existing_roles = session.query(Role).count()
        if existing_roles > 0:
            click.echo("⚠️  Los roles ya existen")
            return
        
        # Crear roles
        user_role = Role(name=RoleEnum.USER.value)
        admin_role = Role(name=RoleEnum.ADMIN.value)
        
        session.add(user_role)
        session.add(admin_role)
        session.commit()
        
        click.echo("✅ Roles creados: user, admin")


@cli.command()
@click.option('--collection', default='documents', help='Nombre de la colección')
def init_vectorstore(collection):
    """Inicializar vector store"""
    click.echo(f"Inicializando vector store: {collection}")
    # Aquí puedes agregar lógica para inicializar el vector store
    click.echo("✅ Vector store inicializado")


if __name__ == "__main__":
    cli()