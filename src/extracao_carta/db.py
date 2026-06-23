"""Conexão PostgreSQL via variáveis de ambiente."""
from __future__ import annotations

import os

import psycopg2
from dotenv import load_dotenv


def load_env(env_path: str = ".env") -> None:
    load_dotenv(env_path)


def connect():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME"),
        client_encoding="UTF8",
    )
