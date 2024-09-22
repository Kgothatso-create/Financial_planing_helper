# create a vertual environment
python3 -m venv financial_oidc

# activate venv
source financial_oidc/bin/activate

# Install packages
pip install django
pip install 
sudo apt install postgresql postgresql-contrib
pip install wheel
pip install psycopg2

# Create a PostgreSQL Database and User
sudo -u postgres psql

CREATE DATABASE finance_oidc;
CREATE USER financeuser WITH PASSWORD 'your_password';
ALTER ROLE financeuser SET client_encoding TO 'utf8';
ALTER ROLE financeuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE financeuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE finance_oidc TO financeuser;

\q

# Change the pg_configs
local   all             postgres                                md5

host    all             all             127.0.0.1/32            md5

