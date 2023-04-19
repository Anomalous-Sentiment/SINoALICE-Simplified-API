from .BaseAPI import BaseAPI
import asyncio
import aiohttp

class GuildAPI(BaseAPI):
    GUILD_RANKS_ENDPOINT = '/api/ranking/guild_ranking'
    GUILD_DATA_ENDPOINT = '/api/guild/guild_data'
    GUILD_MEMBERS_ENDPOINT = '/api/guild/guild_member_list'

    def __init__(self):
        BaseAPI.__init__(self)

    def get_guild_list(self, base_guild_list=[]):
        self._login_account()
        base_list_copy = base_guild_list[:]
        # Call the main async function for getting all guilds and wait for completion
        full_guild_list = asyncio.run(self._get_guild_list_main(base_list_copy))
        return full_guild_list

    def get_selected_guilds(self, base_guild_list):
        self._login_account()
        guild_id_list = []
        # Convert to list of guildDataIds
        for guild in base_guild_list:
            guild_id_list.append(guild['guildDataId'])

        # Get the guild details of the guild Id list
        selected_guild_list = asyncio.run(self._get_selected_guilds_main(guild_id_list))
        return selected_guild_list


    def get_members(self, guild_id):
        member_req_payload = {
            'guildDataId': guild_id
        }

        res = self.post(GuildAPI.GUILD_MEMBERS_ENDPOINT, member_req_payload)
        member_list = res['payload']['guildMemberList']

        return member_list

    def get_guild_data(self, guild_id):
        guild_req_payload = {
            'guildDataId': guild_id
        }

        res = self.post(GuildAPI.GUILD_DATA_ENDPOINT, guild_req_payload)
        guild_data = res['payload']

        
        return guild_data

    async def _get_selected_guilds_main(self, selected_guilds):
        async with aiohttp.ClientSession(BaseAPI.URL) as session:
            selected_guild_list_data = await self._get_full_guild_details(selected_guilds, session)
        return selected_guild_list_data


    async def _get_guild_list_main(self, full_guild_list=[]):
        # Get the guild list for every rank (S, A, B, C, D)
        # Guild ranks are represented as number in requests. (D = 0, C = 1, B = 2, A = 3, S = 4)
        rank_list = [0, 1, 2, 3, 4]

        async with aiohttp.ClientSession(BaseAPI.URL) as session:
            # Call async function to get guilds in rank and wait for all to finish
            guild_rank_lists = await asyncio.gather(*[self._get_rank_guilds(rank, session) for rank in rank_list])

            # Combine lists from every rank for full guild list
            for guild_list in guild_rank_lists:
                full_guild_list.extend(guild_list)

            # convert to set to remove dupicate guildDataIds
            guild_set = set()

            for guild in full_guild_list:
                # Add as dict
                guild_set.add(guild['guildDataId'])

            full_guild_list = await self._get_full_guild_details(guild_set, session)

        return full_guild_list

    async def _get_rank_guilds(self, rank, session):
        guild_rank_list = []

        # This function gets all guilds in a given rank

        init_payload = {
            'countryCode': -1, 
            'mode': 0, 
            'pageNo': 1, 
            'rank': rank, 
            'type': 2
        }

        payload_list = []

        # Make the initial request for the first page of guilds in the given rank
        initial_page_res = await self._async_post(GuildAPI.GUILD_RANKS_ENDPOINT, init_payload, session)

        # Get the total number of pages from the response
        total_pages = initial_page_res['payload']['maxPageNo']

        guild_rank_list.extend(initial_page_res['payload']['guildRankingDataList'])

        if (total_pages > 1):
            # Create a list of payloads to get each page remaining
            for page in range(2, total_pages + 1):
                new_payload = {
                    'countryCode': -1, 
                    'mode': 0, 
                    'pageNo': page, 
                    'rank': rank, 
                    'type': 2
                }

                payload_list.append(new_payload)

            # Send a request to retrieve every page asynchronously
            remainder_pages_res_list = await asyncio.gather(*[self._async_post(GuildAPI.GUILD_RANKS_ENDPOINT, payload, session) for payload in payload_list])

            # Join all pages together for list of all guilds in the given rank
            for res in remainder_pages_res_list:
                guild_rank_list.extend(res['payload']['guildRankingDataList'])
        
        return guild_rank_list

    async def _get_full_guild_details(self, guild_id_set, session):
        payload_list = []
        res_list = []

        # Create list of payloads
        for guild_id in guild_id_set:
            guild_req_payload = {
                'guildDataId': guild_id
            }
            payload_list.append(guild_req_payload)

        for chunk in self._chunks(payload_list, 500):
            # Get full guild details of guild in guild list
            temp_list = await asyncio.gather(*[self._async_post(GuildAPI.GUILD_DATA_ENDPOINT, payload, session) for payload in chunk])
            res_list.extend(temp_list)

        final_guild_data_list = []
        # Extract guild data from rseponses and append to list if not errors
        for res, guild_id in zip(res_list, guild_id_set):
            # Check for errors
            if 'errors' in res:
                # Maybe do error handling. Just print for now
                print('Error getting guild: ' + str(guild_id))
                print(res)
            else:
                final_guild_data_list.append(res['payload']['guildData'])

        return final_guild_data_list

     # From stack overflow. 
    def _chunks(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n] #