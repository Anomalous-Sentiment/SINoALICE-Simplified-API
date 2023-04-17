
from .GuildAPI import GuildAPI
import asyncio
import aiohttp

import json
class PlayerAPI(GuildAPI):
    PLAYER_DATA_ENDPOINT = '/api/profile/get_alice_target_profile_data'

    def __init__(self):
        GuildAPI.__init__(self)

    def get_selected_player_data(self, player_id_list):
        player_list = asyncio.run(self._get_basic_player_info_main(player_id_list))
        return player_list


    def get_players_in_guilds(self, guild_list = None):
        # This function currently depends on using the guild list to retrieve a list of players
        # This is a flawed approach as not all guilds are returned in the call, and not all players are in a guild
        # But this is the only approach I can think of for now aside from brute forcing it and trying every possible
        # User id
        self._login_account()
        if guild_list == None:
            # If no guild list passed in, use GuildAPI functions to get a guild list
            guild_list = asyncio.run(self._get_guild_list_main())

        player_list = asyncio.run(self._get_players_main(guild_list))

        return player_list


    async def get_player_data(self, user_id):
        player_req_payload = {
            'targetUserId': user_id
        }

        res = self.post(PlayerAPI.PLAYER_DATA_ENDPOINT, guild_req_payload)

        return res['payload']

    async def _get_players_main(self, guild_list = None):
        player_list = []
        member_req_payloads = []
        player_data_payloads = []
        player_data_res_list = []

        # Create list of payloads for getting member lists of all guilds
        for guild in guild_list:
            new_member_payload = {
                'guildDataId': guild['guildDataId']
            }

            member_req_payloads.append(new_member_payload)

        async with aiohttp.ClientSession(GuildAPI.URL) as session:
            # For every guild in list, get the member list asynchronously
            member_res_list = await asyncio.gather(*[self._async_post(GuildAPI.GUILD_MEMBERS_ENDPOINT, payload, session) for payload in member_req_payloads])

            # Add the member list to the player list
            for idx, res in enumerate(member_res_list):
                # Check if there is a payload
                if 'payload' in res:
                    player_list.extend(res['payload']['guildMemberList'])
                else:
                    # To implement error handling. Failed to get list for some reason
                    print('Failed to get member list: ', str(res), '. Guild id: ', str(guild_list[idx]['guildDataId']), '. Guild name: ', str(guild_list[idx]['guildName']))

        return player_list

    async def _get_basic_player_info_main(self, player_id_list):
        player_data_res_payload_list = []
        player_data_payloads = []

        # Create a list of payloads for getting player data of every player in list
        for player_id in player_id_list:
            new_player_data_payload = {
                'targetUserId': player_id
            }

            player_data_payloads.append(new_player_data_payload)

        async with aiohttp.ClientSession(GuildAPI.URL) as session:
            # Split requests into chucks to avoid disconnect from server
            for chunk in self._chunks(player_data_payloads, 500):
                # For each member, call the API endpoint to get their player data
                temp_list = await asyncio.gather(*[self._async_post(PlayerAPI.PLAYER_DATA_ENDPOINT, payload, session) for payload in chunk])

                # Add the payloads of each res body to the list
                for res in temp_list:
                    if 'payload' in res:
                        player_data_res_payload_list.append(res['payload'])
                    else:
                        # Error with request
                        print(res)

        return player_data_res_payload_list

    def get_basic_player_info(self, player_list=[]):
        basic_player_data_list = asyncio.run(self._get_basic_player_info_main(player_list))
        return basic_player_data_list