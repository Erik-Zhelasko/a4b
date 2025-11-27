# 1. Setup environment (example)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# 2. Setup database (example)
createdb my_company_db
export DATABASE_URL="postgresql://user:pass@localhost/my_company_db"
# 3. Load schema and your additions

psql -d $DATABASE_URL -f company_v3.02.sql
psql -d $DATABASE_URL -f team_setup.sql

# 4. Run the app
python3 app.py