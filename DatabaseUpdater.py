from api.GuildAPI import GuildAPI
from api.PlayerAPI import PlayerAPI
from api.GranColoAPI import GranColoAPI
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.dialects.postgresql import insert
import psycopg2
from dotenv import load_dotenv

class DatabaseUpdater():
    def __init__():
        pass

    def run(self):
        pass

    def _update_guilds(self):
        pass

    def _update_players(self, guild_list):
        pass

    def _update_gc_ranks(self, day, time):
        pass