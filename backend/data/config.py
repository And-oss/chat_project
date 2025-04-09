import os

class Config:
    SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:1$EgorMySQL@127.0.0.1/test"
    SQLALCHEMY_TRACK_MODIFICATIONS=False

    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USERNAME='as2504684@gmail.com'
    MAIL_PASSWORD='fasf tami jstz jpls'
    MAIL_DEFAULT_SENDER='as2504684@gmail.com'