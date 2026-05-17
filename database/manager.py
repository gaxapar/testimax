from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .models import Base


class ConnectionUrl:
    url_pattern = "postgresql+{connector}://{user}:{password}@{host}/{db_name}"

    def __init__(self, user: str, password: str, db_name: str, host: str) -> None:
        self.data = {"user": user, "password": password, "db_name": db_name, "host": host}

    @property
    def sync_url(self) -> str:
        data = self.data.copy()
        data["connector"] = "psycopg2"

        return self.url_pattern.format(**data)

    @property
    def async_url(self) -> str:
        data = self.data.copy()
        data["connector"] = "asyncpg"

        return self.url_pattern.format(**data)


class DatabaseManager:
    def __init__(self, user: str, password: str, db_name: str, host: str) -> None:
        self.url = ConnectionUrl(user=user, password=password, db_name=db_name, host=host)
        self.base = Base

        self.engine = create_async_engine(url=self.url.async_url)
        self.session = async_sessionmaker(bind=self.engine, expire_on_commit=False)
