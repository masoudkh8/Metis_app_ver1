# 🚀 Complete PostgreSQL Setup Guide

## ✅ Current Project Status
The project is fully configured to use **PostgreSQL** with no SQLite dependencies.

---

## 📋 Setup Steps

### 1. Install PostgreSQL (if not installed)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Create Database and User

```bash
# Login to PostgreSQL
sudo -u postgres psql

# SQL commands to create database and user
CREATE DATABASE ports_db;
CREATE USER ports_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ports_db TO ports_user;
\q
```

### 3. Configure `.env` File

Edit the `.env` file and set `DATABASE_URL`:

```env
DATABASE_URL=postgresql://ports_user:your_secure_password@localhost:5432/ports_db
```

**Real example:**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ports_db
```

### 4. Install Required Libraries

```bash
pip install -r requirements.txt
```

The `psycopg2-binary` library is already included in `requirements.txt`.

### 5. Create Tables in PostgreSQL

```bash
python init_postgres_db.py
```

This script:
- Drops all existing tables (for clean start)
- Creates new tables in PostgreSQL
- Does not insert any data

### 6. Load Port Data (Optional)

If you want to load port data from JSON file:

```bash
python load_ports_to_postgres.py
```

### 7. View Database (Optional)

To view tables and data:

```bash
python view_db.py
```

### 8. Run the Project

```bash
python app.py
```

Or with gunicorn:

```bash
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

---

## 🔧 Available Scripts

| Script | Description |
|---------|-------|
| `init_postgres_db.py` | Create empty tables in PostgreSQL |
| `load_ports_to_postgres.py` | Load port data from JSON |
| `view_db.py` | View database tables and data |

---

## ⚠️ Important Notes

1. **Complete SQLite Removal**: 
   - The `config.py` file no longer supports SQLite
   - The application will error if `DATABASE_URL` is not set

2. **Models**: 
   - All models in the `models/` folder are defined with SQLAlchemy
   - Fully compatible with PostgreSQL

3. **Migrations**: 
   - Flask-Migrate is used for migration management
   - Useful commands:
     ```bash
     flask db init          # Only first time
     flask db migrate -m "description"
     flask db upgrade
     ```

4. **Create Admin**:
   ```bash
   flask create-admin
   ```

---

## 🎯 Quick Command Summary

```bash
# 1. Setup database
echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ports_db" >> .env

# 2. Create tables
python init_postgres_db.py

# 3. Load data (optional)
python load_ports_to_postgres.py

# 4. View database
python view_db.py

# 5. Run application
python app.py
```

---

## 📞 Support

If you encounter any errors:
1. Make sure PostgreSQL is running: `sudo systemctl status postgresql`
2. Check that `DATABASE_URL` in `.env` is correct
3. Review logs in `logs/app.log`
