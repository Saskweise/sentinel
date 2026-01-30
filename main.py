from typing import Union
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from log import Log

app = FastAPI()

CSV_FILE = 'access_logs.csv'

# Ejemplo de cómo crear una clase para la API
# class Item(BaseModel):
#     name: str
#     price: float
#     is_offer: Union[bool, None] = None

@app.get("/")
# Devuelve un JSON al acceder a la raíz
def read_root():
    return f"Bienvenido a la interfaz de Sentinel!"

# Ejemplo de cómo devolver un JSON al tratar de acceder a un directorio
# @app.get("/items/{item_id}")
# Union es una función de Pydantic que valida el argumento
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}

# Ejemplo de cómo actualizar el item que le envíes
# @app.put("/items/{item_id}")
# def update_item(item_id: int, item: Item):
#     return {"item_name": item.name, "item_id": item_id}

# Actualiza CSV_FILE con el log correspondiente
@app.post("/logs")
def create_log(log: Log):
    data = {
        # Hay que poner entre corchetes para pandas
        "source" : [log.ip],
        "route" : [log.route],
        "date" : [log.timestamp],
        "code" : [log.code_response]
        }
    
    # Convierte en dataframe de pandas
    # Index y Header en false para que añada las filas solamente
    pd.DataFrame(data).to_csv(CSV_FILE, mode='a', index= False, header= False)

    print(f"New IP added to access_logs.py: {log.ip}")
    return {"message": "OK!"}

# Devuelve JSON con información de los logs
@app.get("/status")
def get_status():
    # Hay que pasarle las keys entre [] porque no pusimos headers
    df = pd.read_csv(CSV_FILE, names = ['source', 'route', 'date', 'code']) 
    # Conteo de logs
    total_logs = len(df)
    # Devuelve el número de ips únicas
    unique_ips = df["source"].nunique()
    # Devuelve el número de peticiones con código > 400
    errors = len(df.query('code > 400'))

    return {
        "total_logs" : total_logs,
        "unique_ips" : unique_ips,
        "errors_amount" : errors
    }

# Devuelve JSON con las peticiones de cada ip
@app.get("/ip-queries")
def get_queries():
    df = pd.read_csv(CSV_FILE, names= ['source', 'route', 'date', 'code'])
    # Sortea por ip y directorio al que intenta acceder
    # Debe convertirse a diccionario porque el objeto que da pandas no es un dict
    q_by_ip = df.groupby('source')['route'].size().to_dict()
    only_errors = df[df['code'] >= 400]
    errors = only_errors.groupby('source').size()
    return {
        "Queries by IP" : q_by_ip,
        "403 Queries" : errors.to_dict()
    }

# Devuelve JSON con con ips y estadísticas
@app.get("/analyze")
def get_analysis():
    df = pd.read_csv(CSV_FILE, names= ['source', 'route', 'date', 'code'])
    # Sorteamos por ip y su número de peticiones
    queries =  df.groupby('source').size()
    # Sorteamos por aquellas ip con código mayor que 400
    errors = df[df['code'] > 400].groupby('source').size()

    # Combinamos ambos resultados en un dataframe
    # fillna(0) sustituye los 'NaN' por 0 para que mantenga el formato JSON
    # astype(int) muestra las queries en enteros, sino las muestra en float por los NaN
    summary = pd.DataFrame({"queries" : queries, "errors" : errors}).fillna(0).astype(int)

    # orient='index' hace que se filtren por ip
    # anteriormente ya lo habíamos filtrado por ip, solo lo combinamos
    return summary.to_dict(orient= "index")