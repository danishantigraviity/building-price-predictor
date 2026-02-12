import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:////tmp/site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 2026 Prediction Config
    INFLATION_RATE = 0.07 # 7% growth per year

    # Mail Config (SMTP)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'danishappu33@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'kmor wemo zzch dnhi')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'danishappu33@gmail.com')
