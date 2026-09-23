from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    mysql_database: str
    mysql_user: str
    mysql_password: str
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> URL:
        return URL.create(
            "mysql+pymysql",
            username=self.mysql_user,
            password=self.mysql_password,
            host=self.mysql_host,
            port=self.mysql_port,
            database=self.mysql_database,
        )


settings = Settings()