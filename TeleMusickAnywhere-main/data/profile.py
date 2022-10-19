import sqlalchemy

from .db_session import SqlAlchemyBase


class Users(SqlAlchemyBase):  # класс добавляемойс cтрочки
    __tablename__ = 'user_profile'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)  # генерируемый id
    user_id = sqlalchemy.Column(sqlalchemy.String)  # id пользователя
    listen_statistic = sqlalchemy.Column(sqlalchemy.String)  # статистика пользователя
    add_statistic = sqlalchemy.Column(sqlalchemy.String)  # статистика пользователя
    ads_statistic = sqlalchemy.Column(sqlalchemy.String)  # статистика пользователя
    user_playlist = sqlalchemy.Column(sqlalchemy.String)  # плейлист пользователя
