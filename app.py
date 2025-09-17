import os
from flask import Flask, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL")
PORT = int(os.getenv("PORT", "8002"))

engine = create_engine(DB_URL, pool_pre_ping=True, future=True)
app = Flask(__name__)

@app.get("/")
def root():
    return {"status": "ok", "app": "MGComputacion API"}

@app.get("/dbcheck")
def dbcheck():
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS hello(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    msg VARCHAR(100) NOT NULL
                ) ENGINE=InnoDB;
            """))
            conn.execute(text("INSERT INTO hello(msg) VALUES ('hola mgcomputacion')"))
            row = conn.execute(text("SELECT COUNT(*) AS c FROM hello")).one()
        return jsonify(ok=True, rows=row.c)
    except SQLAlchemyError as e:
        return jsonify(ok=False, error=str(e)), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
