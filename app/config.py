class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@127.0.0.1/dentista_db";
    JWT_SECRET_KEY = "thisismysecret"
    JWT_ACCESS_TOKEN_EXPIRES = False