from BaseAPI import BaseAPI
from GuildAPI import GuildAPI
import asyncio
import aiohttp

class PlayerAPI(GuildAPI):
    def __init__(self):
        GuildAPI.__init__(self)

    def get_players(self):
        pass

    async def get_player_data(self):
        pass