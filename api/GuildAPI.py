from BaseAPI import BaseAPI
import asyncio
import aiohttp

class GuildAPI(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)

    def get_guild_list(self):
        # Call the main async function for getting all guilds and wait for completion
        pass

    def get_members(self, guild_id):
        pass

    def get_guild_data(self, guild_id):
        pass

    async def _get_guild_list_main(self):
        # Get the guild list for every rank (S, A, B, C, D)
        # Guild ranks are represented as number in requests. (D = 0, C = 1, B = 2, A = 3, S = 4)

        # Combine lists from every rank for full guild list


        pass

    async def _get_rank_guilds(self, rank):
        # This function gets all guilds in a given rank

        # Make the initial request for the first page of guilds in the given rank

        # Get the total number of pages from the response

        # Send a request for every page asynchronously

        # Join all pages together for list of all guilds in the given rank

        pass