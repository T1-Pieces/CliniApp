
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-desarrollo-local")

    MYSQL_HOST = os.getenv("DB_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("DB_PORT", 3306))
    MYSQL_USER = os.getenv("DB_USER", "root")
    MYSQL_PASSWORD = os.getenv("DB_PASSWORD")
    MYSQL_DATABASE = os.getenv("DB_NAME", "cliniapp")
