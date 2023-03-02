from BaseAPI import BaseAPI
from GuildAPI import GuildAPI
import asyncio
import aiohttp

class PlayerAPI(GuildAPI):
    PLAYER_DATA_ENDPOINT = '/api/profile/get_alice_target_profile_data'

    def __init__(self):
        GuildAPI.__init__(self)

    def get_players(self, guild_list = None):
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

    async def get_player_data(self):
        pass

    async def _get_players_main(self, guild_list = None):
        player_list = []
        member_req_payloads = []
        player_data_payloads = []

        # Create list of payloads for getting member lists of all guilds
        for guild in guild_list:
            new_member_payload = {
                'guildDataId': guild['guildDataId']
            }

            member_req_payloads.append(new_member_payload)

        async with aiohttp.ClientSession(BaseAPI.URL) as session:
            # For every guild in list, get the member list asynchronously
            member_res_list = await asyncio.gather(*[self._async_post(GuildAPI.GUILD_MEMBERS_ENDPOINT, payload, session) for payload in member_req_payloads])

            # Add the member list to the player list
            for res in member_res_list:
                # Check if there is a payload
                if 'payload' in res:
                    player_list.extend(res['payload']['guildMemberList'])
                else:
                    # To implement error handling. Failed to get list for some reason
                    print('Failed to get member list: ', str(res))

            # Create a list of payloads for getting player data of every player in list
            for player in player_list:
                new_player_data_payload = {
                    'targetUserId': player['guildUserData']['userId']
                }

                player_data_payloads.append(new_player_data_payload)

            # For each member, call the API endpoint to get their player data
            player_data_res_list = await asyncio.gather(*[self._async_post(PlayerAPI.PLAYER_DATA_ENDPOINT, payload, session) for payload in player_data_payloads])

            # Combine the data
            for guild_player_data, player_res_data in zip(player_list, player_data_res_list):
                # Combine dicts
                guild_player_data['userData'].update(player_res_data['payload'])

        return player_list

