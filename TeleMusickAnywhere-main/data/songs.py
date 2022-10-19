import sqlalchemy

from .db_session import SqlAlchemyBase


class Song(SqlAlchemyBase):  # класс добавляемойс трочки
    __tablename__ = 'songs'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)  # генерируемый id
    name = sqlalchemy.Column(sqlalchemy.String, index=True)  # название песни
    photo = sqlalchemy.Column(sqlalchemy.String, index=True)  # изображение песни
    qr = sqlalchemy.Column(sqlalchemy.String)  # ее qr, поменять на блоб
    gif = sqlalchemy.Column(sqlalchemy.String)  # фоточка, тут лежит гифка с диском
    song = sqlalchemy.Column(sqlalchemy.String)  # id песни
    text = sqlalchemy.Column(sqlalchemy.String, index=True)  # текст песни
    author = sqlalchemy.Column(sqlalchemy.String)  # id автора
    audio_location = sqlalchemy.Column(sqlalchemy.String)  # Местоположение песни
