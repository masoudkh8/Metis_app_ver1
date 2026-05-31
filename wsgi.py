# wsgi.py
# این فایل را در کنار app.py بسازید
# ایجاد اپلیکیشن برای محیط production


from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()