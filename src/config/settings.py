from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    service_name: str = "siglog-customer"
    database_url: str = "postgresql+psycopg://siglog:siglog_dev@localhost:5432/siglog_customer"
    rabbitmq_url: str = "amqp://siglog:siglog_dev@localhost:5672/"


settings = Settings()
