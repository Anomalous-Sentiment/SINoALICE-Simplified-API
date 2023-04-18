from .BaseAPI import BaseAPI
import asyncio
import aiohttp

class GranColoAPI(BaseAPI):
    GC_ENDPOINT = '/api/gvg_event/get_gvg_event_ranking'

    def __init__(self):
        BaseAPI.__init__(self)

    def get_ts_rank_list(self, ts):
        self._login_account()
        ts_list = asyncio.run(self._get_ts_rank_list_main(ts))
        return ts_list

    def get_full_rank_list(self):
        self._login_account()
        final_list = asyncio.run(self._get_full_rank_list_main())
        return final_list

    def get_next_gc_dates(self):
        pass

    async def _get_top_50_guilds(self, ts, session):
        init_payload = {
            'guildDataId': 0,
            'gvgTimeType': ts,
            'leagueId': 1,
            'pageNo': 0
        }

        
        # Expected to return 50 guilds
        response = await self._async_post(GranColoAPI.GC_ENDPOINT, init_payload, session=session)


        top_50_list = response['payload']['gvgEventRankingDataList']

        return top_50_list

    async def _get_next_10_guilds(self, ts, last_guild_id, session):
        rev_rank_payload = {
            'guildDataId': last_guild_id,
            'gvgTimeType': ts,
            'leagueId': 1,
            'pageNo': 0
        }


        response = await self._async_post(GranColoAPI.GC_ENDPOINT, rev_rank_payload, session=session)

        temp_21_list = response['payload']['gvgEventRankingDataList']

        new_index = 10

        # Check if last guild id is at expected location. The last_guild_id should be at idx 10. If not, then
        # we may have hit the end of the list.
        # Find the index of the last guild Id if not at expected location
        while temp_21_list[new_index]['guildDataId'] != last_guild_id:
            new_index = new_index + 1


        # Return the list of guilds that come after last_guild_id. Usually 10, but will be less than 10 if there are less than 10 guilds before end the of ranking list
        return temp_21_list[new_index + 1::]

    async def _get_full_ts_ranks(self, ts, top_50_list, session):
        ts_guild_list = top_50_list
        
        # Get the next 10 guilds using last guild Id
        next_10_guilds = await self._get_next_10_guilds(ts, top_50_list[-1]['guildDataId'], session=session)

        # Add the guilds to the ts list
        ts_guild_list.extend(next_10_guilds)

        new_guilds_in_list = [False]

        # Iterate until less than 10 guilds returned. If less than 10 guilds, then that is the end of the list. Also exist if all of nect guilds are in list already to avoid infinite loop (May occur when there are more than 10 guilds with same rank at the bottom?? Just a safety measure)
        while len(next_10_guilds) >= 10 or any(new_guilds_in_list):

            #Get the next 10 guilds again
            next_10_guilds = await self._get_next_10_guilds(ts, ts_guild_list[-1]['guildDataId'], session=session)

            new_guilds_in_list = []

            for new_guild in next_10_guilds:
                if new_guild not in ts_guild_list:
                    # Append to list
                    ts_guild_list.append(new_guild)
                    new_guilds_in_list.append(True)
                else:
                    new_guilds_in_list.append(False)

        # Return the final list
        return ts_guild_list

    async def _get_full_rank_list_main(self):
        gc_time_slots = [3, 4, 5, 6, 7, 8, 9, 10, 12, 13]
        final_list = []

        async with aiohttp.ClientSession(BaseAPI.URL) as session:
            # Returns a list of list of guilds
            all_ts_top_50 = await asyncio.gather(*[self._get_top_50_guilds(ts, session) for ts in gc_time_slots])

            # Get the remainder of the ranking list for each ts
            fulls_ts_list = await asyncio.gather(*[self._get_full_ts_ranks(ts, top_50, session) for ts, top_50 in zip(gc_time_slots, all_ts_top_50)])

            # Join the lists of each ts together into final list
            for ts_list in fulls_ts_list:
                final_list.extend(ts_list)

        return final_list

    async def _get_ts_rank_list_main(self, ts):
        async with aiohttp.ClientSession(BaseAPI.URL) as session:
            # Returns a list of list of guilds
            ts_top_50 = await self._get_top_50_guilds(ts, session)

            # Get the remainder of the ranking list for each ts
            full_ts_list = await self._get_full_ts_ranks(ts, ts_top_50, session)

        return full_ts_list