from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

	togolm_api_key: str = ""
	togolm_base_url: str = "https://api.togolm.com/v1"
	ollama_base_url: str = "http://127.0.0.1:11434"
	ollama_model: str = "gemma3:1b"
	# Google AI Studio key → hosted Gemma (Best Use of Gemma)
	gemini_api_key: str = ""
	gemma_cloud_model: str = "gemma-4-26b-a4b-it"
	cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
	host: str = "127.0.0.1"
	port: int = 8000

	@property
	def cors_origin_list(self) -> list[str]:
		return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
	return Settings()
