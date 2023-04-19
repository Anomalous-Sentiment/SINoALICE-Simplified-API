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

    async def _get_surrounding_guilds(self, ts, last_guild_id, session):
        rev_rank_payload = {
            'guildDataId': last_guild_id,
            'gvgTimeType': ts,
            'leagueId': 1,
            'pageNo': 0
        }


        response = await self._async_post(GranColoAPI.GC_ENDPOINT, rev_rank_payload, session=session)

        temp_21_list = response['payload']['gvgEventRankingDataList']

        # Return the list of guilds that come after last_guild_id. Usually 10, but will be less than 10 if there are less than 10 guilds before end the of ranking list
        return temp_21_list

    async def _get_full_ts_ranks(self, ts, top_50_list, session):
        ts_guild_list = top_50_list

        # Sort guilds in case the LF has updated, but rankings have not
        ts_guild_list = sorted(ts_guild_list, key=lambda d: d['point'], reverse=True)
        
        # Get the guilds surrounding the top guild
        surrounding_guilds = await self._get_surrounding_guilds(ts, top_50_list[0]['guildDataId'], session=session)

        # Use the guilds surrounding the top 1 guild of TS as the base list
        ts_guild_list = surrounding_guilds

        ts_guild_list = await self._iterate_through_rankings(ts, ts_guild_list, session)
        ts_guild_list = await self._iterate_through_rankings(ts, ts_guild_list, session, reverse=True)

        # Filter out duplicates (Safety measure)
        ts_guild_list = {frozenset(item.items()) : item for item in ts_guild_list}.values()

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

    async def _iterate_through_rankings(self, ts, ts_guild_list, session, reverse=False):
        # If reverse is true, then get all guilds higher than the guild with highest LF in list,
        # Else go down the rankings from highest LF to lowest
        index = -1

        if reverse is True:
            index = 0

        new_guilds_in_list = [True]

        # Get guilds from the specified starting point of list. Repeat until all surrounding guilds are already in list
        while any(new_guilds_in_list):
            # Sort again for same reason as previously
            ts_guild_list = sorted(ts_guild_list, key=lambda d: d['point'], reverse=True)

            #Get the surrounding guilds of the first/last guild of the current TS list depending on reverse value
            surrounding_guilds = await self._get_surrounding_guilds(ts, ts_guild_list[index]['guildDataId'], session=session)
            surrounding_guilds = sorted(surrounding_guilds, key=lambda d: d['point'], reverse=True)


            new_guilds_in_list = []

            # Only add surrounding guild to list if not in list already
            for new_guild in surrounding_guilds:
                if not any(d['gvgEventRankingDataId'] == new_guild['gvgEventRankingDataId'] for d in ts_guild_list):
                    # Append to list
                    ts_guild_list.append(new_guild)
                    new_guilds_in_list.append(True)
                else:
                    new_guilds_in_list.append(False)

        ts_guild_list = sorted(ts_guild_list, key=lambda d: d['point'], reverse=True)
        return ts_guild_list