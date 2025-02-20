class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://austin:root@localhost:5433/hazina_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key-here'