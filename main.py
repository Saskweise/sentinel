import os
from typing import Union
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from log import Log

app = FastAPI()

# File where logs are added
CSV_FILE = 'access_logs.csv'

# If CSV_FILE doesn't exists, it is created
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=['source', 'route', 'date', 'code'])
    df = df.to_csv(CSV_FILE, index=False, header=False)
    print(f"{CSV_FILE} has been created successfully.")


# Returns a JSON when entering the root
@app.get("/")
def read_root():
    return f"Sentinel Online."

# Updates CSV_FILE with a log
@app.post("/logs")
def create_log(log: Log):
    data = {
        # Brackets must be used in order to use pandas
        "source" : [log.ip],
        "route" : [log.route],
        "date" : [log.timestamp],
        "code" : [log.code_response]
        }
    
    # Creates a panda's dataframe
    # Index and Header are false in order to only add the rows
    pd.DataFrame(data).to_csv(CSV_FILE, mode='a', index= False, header= False)

    print(f"New IP added to access_logs.py: {log.ip}")
    return {"message": "OK!"}

# Returns a JSON with logs information
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

    # Creamos un diccionario que agrupa las rutas por ip
    # fillna(0) sustituye los 'NaN' por 0 para que mantenga el formato JSON
    # astype(int) muestra las queries en enteros, sino las muestra en float por los NaN
    routes = df.groupby(['source', 'route']).size().unstack().fillna(0).astype(int)
    # Las rutas las convertimos en un diccionario
    routes = routes.to_dict(orient='index')

    # Combinamos ambos resultados en un dataframe
    summary = pd.DataFrame({"queries" : queries, "errors" : errors}).fillna(0).astype(int)
    summary = summary.to_dict(orient='index')

    # Adds a route dictionary to every key, if it's null, it adds an empty dict
    for ip in summary:
        summary[ip]["routes"] = routes.get(ip, {})

    return summary