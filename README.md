## Database Setup

createdb company

## Load Company Schema

psql company < /path/to/company_v3.02.sql

## Load team_setup_sql

psql company < team_setup.sql


## Admin login:

username: admin
password: admin123

## Viewer login:

username: viewer
password: viewer123

## Running the Application
From inside the project folder, type 

***python3 app.py***

### then visit http://127.0.0.1:5000/