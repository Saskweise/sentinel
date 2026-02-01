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
    df = pd.read_csv(CSV_FILE, names = ['source', 'route', 'date', 'code']) 
    # logs count
    total_logs = len(df)
    # Returns the amount of unique ips
    unique_ips = df["source"].nunique()
    # Returns the amount of ips with code >= 400
    errors = len(df.query('code >= 400'))

    return {
        "total_logs" : total_logs,
        "unique_ips" : unique_ips,
        "errors_amount" : errors
    }

# Returns a JSON with ip queries
@app.get("/ip-queries")
def get_queries():
    df = pd.read_csv(CSV_FILE, names = ['source', 'route', 'date', 'code']) 
    # Sorts by ip and path that are being entered
    # Must be converted to dict due to json api format
    q_by_ip = df.groupby('source')['route'].size().to_dict()
    only_errors = df[df['code'] >= 400]
    errors = only_errors.groupby('source').size()
    return {
        "Queries by IP" : q_by_ip,
        "403 Queries" : errors.to_dict()
    }

# Returns a JSON with metrics
@app.get("/analyze")
def get_analysis():
    try:
        df = pd.read_csv(CSV_FILE, names = ['source', 'route', 'date', 'code']) 

        # Sorts by ip and query amount
        queries =  df.groupby('source').size()

        # Sorts by ip with code >= 400
        errors = df[df['code'] >= 400].groupby('source').size()

        # dict that groups path by ip
        # fillna(0) replaces ‘NaN’ with 0 to maintain the JSON format
        # astype(int) displays queries as integers; otherwise, they are displayed as floats due to NaN
        routes = df.groupby(['source', 'route']).size().unstack().fillna(0).astype(int)
        # Paths are converted into dicts
        routes = routes.to_dict(orient='index')

        # Results are merged into a dataframe
        summary = pd.DataFrame({"queries" : queries, "errors" : errors}).fillna(0).astype(int)
        summary = summary.to_dict(orient='index')

        # Adds a route dictionary to every key, if it's null, it adds an empty dict
        for ip in summary:
            summary[ip]["routes"] = routes.get(ip, {})

        return summary
    except Exception as e:
        return {"error": str(e)}

@app.get("/queries")
def get_queries():
    try:
        df = pd.read_csv(CSV_FILE, names = ['source', 'route', 'date', 'code'])
        # It converts the column into datetime format
        df['date'] = pd.to_datetime(df['date'])
        # A new column is created in order to groupby it later
        # It must be converted to str, otherwise it becomes an object type, we need str
        df['min'] = df['date'].dt.floor('min').astype(str)
        # unstack is used in order to group it into a matrix
        # fill_value=0 does the same work as fill.na(0) but it does it in one execution
        q_per_min = df.groupby(['source', 'min']).size().unstack(fill_value=0)
        q_per_min = q_per_min.to_dict(orient='index')
        return q_per_min
    
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/complete")
def get_complete():
    try:
        df = pd.read_csv(CSV_FILE, names = ['source', 'route', 'date', 'code'])

        queries = df.groupby('source').size().rename("Total Queries")# So that column isn't named 0
        errors = df[df['code'] >= 400].groupby('source').size().rename("Total Errors")
        paths = df.groupby('source')['route'].nunique().rename("Unique Paths")

        df['date'] = pd.to_datetime(df['date'])
        df['min'] = df['date'].dt.floor(('min')).astype(str)

        speed = df.groupby(['source', 'min']).size()
        avg_speed = speed.groupby('source').mean().rename("Average QPM")
        summary = pd.concat([queries, errors, paths, avg_speed], axis=1).fillna(0).astype(int)
        summary = summary.to_dict(orient='index')
        return summary

    except Exception as e:
        return {"error": str(e)}