from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    service_name: str = "siglog-customer"
    database_url: str = "postgresql+psycopg://siglog:siglog_dev@localhost:5432/siglog_customer"
    # Pool de conexões: espera curta por uma conexão livre e resposta 503 (em vez de travar threads por 30 s sob carga)
    db_pool_size: int = 10
    db_max_overflow: int = 10
    db_pool_timeout: int = 5
    rabbitmq_url: str = "amqp://siglog:siglog_dev@localhost:5672/"
    jwt_secret: str = ""
    jwt_leeway_seconds: int = 30  # tolerância de relógio (iat/exp); containers costumam ficar alguns segundos defasados
    supabase_url: str = ""  # ex.: https://<ref>.supabase.co (habilita tokens ES256/RS256 via JWKS)
    tracking_base_url: str = ""
    tracking_mock: bool = False  # demo: rastreamento simulado enquanto o contrato do Tracking não existe
    # chave Fernet (urlsafe base64) para cifrar chaves de API de integração; vazio = não permite salvar chaves
    settings_encryption_key: str = ""
    cors_origins: str = ""  # origens do front separadas por vírgula (ex.: https://portal.pages.dev)
    events_exchange: str = "siglog.events"
    otel_exporter_otlp_endpoint: str = ""  # vazio = tracing desligado
    worker_metrics_port: int = 9100


settings = Settings()
