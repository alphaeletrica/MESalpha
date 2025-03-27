import sqlite3
from contextlib import contextmanager
import os

class DatabaseHandler:
    def __init__(self, db_path='mesalpha.db'):
        self.db_path = db_path
        self.initialize_db()
    
    def initialize_db(self):
        with self.get_connection() as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    role TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS maquinas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    last_maintenance TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS paradas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    machine_id INTEGER NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    reason TEXT NOT NULL,
                    FOREIGN KEY (machine_id) REFERENCES machines (id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS tarefas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    due_date TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS ProducaoSoja (
                    ID INT PRIMARY KEY,
                    Data DATE NOT NULL,
                    UmidadeSoja DECIMAL(4, 2) NOT NULL,
                    ProteinaBrutaSoja DECIMAL(4, 2) NOT NULL,
                    ImpurezasSoja DECIMAL(4, 2) NOT NULL,
                    ProducaoDiaria DECIMAL(10, 2) NOT NULL,
                    ProducaoMensal DECIMAL(10, 2) NOT NULL                );

                CREATE TABLE IF NOT EXISTS FareloSojaTostado (
                    ID INT PRIMARY KEY,
                    Data DATE NOT NULL,
                    UmidadeFarelo DECIMAL(4, 2) NOT NULL,
                    ProteinaBrutaFarelo DECIMAL(4, 2) NOT NULL,
                    GorduraFarelo DECIMAL(4, 2) NOT NULL                );
            ''')

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

