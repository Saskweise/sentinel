Sentinel is an intelligent system designed to monitorize web traffic and detect suspicious behavior through ML. It utilizes a modern architecture based on FastAPI to read data and Isolation Forest to identify anomalies.



Sentinel State:

Sentinel is on the data entry pase.



\[X] Week 1: API and environment settings.

\[X] Week 2: Logs simulation and persistent storage (CSV).

\[ ] Week 3: AI (Isolation Forest) model training.

\[ ] Week 4: Automatic IP block system and Dashboard.



* Language: Python 3.10+
* Framework: FastAPI
* Processing: Pandas
* Simulation: Requests
* Validation: Pydantic



-------------------------------------------------------------------------------------

INSTALLING

----------



1. Clone the repository



git clone https://github.com/Saskweise/sentinel

cd sentinel/backend



2\. Create venv



python -m venv venv

source venv/bin/actívate # Windows option: .\\venv\\Scripts\\Activate.ps1



3\. Install dependencies



pip install -r requirements.txt



-------------------------------------------------------------------------------------

SENTINEL USAGE

--------------



1. Launch server (API)



uvicorn main:app --reload



2\. Simulate traffic



python genereate\_logs.py



3\. Analyze traffic through http://localhost:8000/analyze



-------------------------------------------------------------------------------------

MAIN ENDPOINTS

--------------



* /logs: receives a log and saves it into the dataset.
* /analyze: returns IP statistics, paths and errors.
* /queries: shows a summary about the logs amount.



-------------------------------------------------------------------------------------

DETECTION LOGIC (COMING SOON)

-----------------------------



The system will use an Isolation Forest algorithm to differentiate legitimate traffic with anomalies by using:



* IP queries frequency.
* Errors (403/404).
* Access to prohibited paths.



