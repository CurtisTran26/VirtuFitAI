import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from dotenv import load_dotenv

# Thêm root vào sys.path để import backend modules
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

APP_API_DIR = os.path.join(ROOT_DIR, "backend", "app-api")
if APP_API_DIR not in sys.path:
    sys.path.insert(0, APP_API_DIR)

# Nạp biến môi trường từ .env nếu có
load_dotenv(os.path.join(ROOT_DIR, ".env"))

# Import Base và tất cả models để Alembic nhận diện schema đầy đủ
from backend.shared.database.session import Base
import backend.shared.models  # noqa: F401 - đảm bảo tất cả models được import vào metadata

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# target_metadata cho tính năng autogenerate
target_metadata = Base.metadata

# Lấy DATABASE_URL từ môi trường (ưu tiên) hoặc fallback vào alembic.ini
db_url = os.getenv("DATABASE_URL")
if not db_url:
    # Nếu chạy local mà DB_HOST=postgres (theo docker), chuyển sang localhost khi chạy ngoài container
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_user = os.getenv("DB_USER", "virtufit_user")
    db_pass = os.getenv("DB_PASSWORD", "virtufit_secure_password_dev")
    db_name = os.getenv("DB_NAME", "virtufit_db")
    db_url = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Khởi tạo async engine và thực thi migration."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
