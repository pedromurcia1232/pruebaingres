from flask import Flask, render_template, request
import threading
import pandas as pd
import requests
import io
import main_script  # tu script selenium

app = Flask(__name__)

EXCEL_URL = (
    "https://biotelecomm044-my.sharepoint.com/:x:/g/"
    "personal/pedromurcia_biotelecomm044_onmicrosoft_com/"
    "EZHvFcj17ctGpRo4tU8tf6cBfItr6u9ht_EDYYDhLbbhWA?download=1"
)

@app.route('/')
def index():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username'].strip()
    password = request.form['password'].strip()
    manpack = request.form['manpack'].strip()

    try:
        # Descargar el archivo Excel
        response = requests.get(EXCEL_URL)
        response.raise_for_status()

        # Leer el Excel como texto, quitar filas vacías
        df = pd.read_excel(io.BytesIO(response.content), dtype=str).dropna(how="all")

        # Limpiar espacios en todas las celdas
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    except Exception as e:
        return f"❌ No se puede leer el Excel desde OneDrive: {e}"

    # Filtrar usuario válido
    user = df[
        (df['Usuario'] == username) &
        (df['Contraseña'] == password) &
        (df['Man Pack'] == manpack)
    ]

    if not user.empty:
        alias = user.iloc[0].get("Alias")
        if not alias:
            return f"❌ No se encontró alias para el Man Pack {manpack}."
        threading.Thread(target=main_script.run, args=(alias,)).start()
        return f"✅ Bienvenido, {username}. El script se está ejecutando para el subsite '{alias}'."
    else:
        return "❌ Usuario, contraseña o Man Pack incorrectos."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
