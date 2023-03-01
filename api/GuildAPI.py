from BaseAPI import BaseAPI
import asyncio
import aiohttp

class GuildAPI(BaseAPI):
    GUILD_RANKS_ENDPOINT = '/api/ranking/guild_ranking'
    GUILD_DATA_ENDPOINT = '/api/guild/guild_data'
    GUILD_MEMBERS_ENDPOINT = '/api/guild/guild_member_list'

    def __init__(self):
        BaseAPI.__init__(self)

    def get_guild_list(self):
        # Call the main async function for getting all guilds and wait for completion
        full_guild_list = asyncio.run(self._get_guild_list_main())
        return full_guild_list

    def get_members(self, guild_id):
        pass

    def get_guild_data(self, guild_id):
        pass

    async def _get_guild_list_main(self):
        # Get the guild list for every rank (S, A, B, C, D)
        # Guild ranks are represented as number in requests. (D = 0, C = 1, B = 2, A = 3, S = 4)
        rank_list = [0, 1, 2, 3, 4]
        full_guild_list = []

        async with aiohttp.ClientSession(BaseAPI.URL) as session:
            # Call async function to get guilds in rank and wait for all to finish
            guild_rank_lists = await asyncio.gather(*[self._get_rank_guilds(rank, session) for rank in rank_list])

        # Combine lists from every rank for full guild list
        for guild_list in guild_rank_lists:
            full_guild_list.extend(guild_list)

        return full_guild_list

    async def _get_rank_guilds(self, rank, session):
        # This function gets all guilds in a given rank

        # Make the initial request for the first page of guilds in the given rank
        initial_page_res = self._single_main()

        # Get the total number of pages from the response

        # Send a request for every page asynchronously

        # Join all pages together for list of all guilds in the given rank

        pass