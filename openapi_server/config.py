from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    device: str = "linux"
    application: str = "blahblah"
    version: str = "0.0.11"
    server_crt_path: str = "./crt/cert.pem"

settings = Settings()

