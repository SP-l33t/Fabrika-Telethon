from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str
    GLOBAL_CONFIG_PATH: str = "TG_FARM"

    FIX_CERT: bool = False

    REF_ID: str = "ref_2222195"
    SQUAD_ID: int | None = None

    AUTO_TASK: bool = True

    AUTO_BOOST: bool = True
    AUTO_TAP: bool = True
    TAP_COUNT: list[int] = [50, 200]
    TAP_MIN_ENERGY: int = 50

    AUTO_MANAGE_FACTORY: bool = True
    UPGRADE_WORKPLACES: bool = True
    AUTO_BUY_WORKER: bool = True

    RANDOM_SESSION_START_DELAY: int = 30

    SESSIONS_PER_PROXY: int = 1
    USE_PROXY_FROM_FILE: bool = True
    DISABLE_PROXY_REPLACE: bool = False
    USE_PROXY_CHAIN: bool = False

    DEVICE_PARAMS: bool = False

    DEBUG_LOGGING: bool = False


settings = Settings()

