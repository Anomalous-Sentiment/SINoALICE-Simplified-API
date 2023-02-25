from BaseAPI import BaseAPI


class GranColoAPI(BaseAPI):
    GC_ENDPOINT = '/api/gvg_event/get_gvg_event_ranking'

    def __init__(self):
        BaseAPI.__init__(self)

    def get_ts_rank_list(self, ts):
        # Get the top 50 guilds
        ts_guild_list = self._get_top_50_guilds(ts)

        # Get the next 10 guilds using last guild Id
        next_10_guilds = self._get_next_10_guilds(ts, ts_guild_list[-1]['guildDataId'])

        # Add the guilds to the ts list
        ts_guild_list.extend(next_10_guilds)

        # Iterate until less than 10 guilds returned. If less than 10 guilds, then that is the end of the list
        while len(next_10_guilds) >= 10:

            #Get the next 10 guilds again
            next_10_guilds = self._get_next_10_guilds(ts, ts_guild_list[-1]['guildDataId'])

            # Add the guilds to the ts list
            ts_guild_list.extend(next_10_guilds)

        # Return the final list
        return ts_guild_list

    def get_full_rank_list(self):
        gc_time_slots = [3, 4, 5, 6, 7, 8, 9, 10, 12, 13]
        final_list = []

        for ts in gc_time_slots:
            ts_guild_list = self.get_ts_rank_list(ts)
            final_list.extend(ts_guild_list)
        
        return final_list

    def get_next_gc_dates(self):
        pass

    def _get_top_50_guilds(self, ts):
        init_payload = {
            'guildDataId': 0,
            'gvgTimeType': ts,
            'leagueId': 1,
            'pageNo': 0
        }

        
        # Expected to return 50 guilds
        response = self.post(GranColoAPI.GC_ENDPOINT, init_payload)

        top_50_list = response['payload']['gvgEventRankingDataList']

        return top_50_list

    def _get_next_10_guilds(self, ts, last_guild_id):
        rev_rank_payload = {
            'guildDataId': last_guild_id,
            'gvgTimeType': ts,
            'leagueId': 1,
            'pageNo': 0
        }

        print(last_guild_id)

        response = self.post(GranColoAPI.GC_ENDPOINT, rev_rank_payload)

        temp_21_list = response['payload']['gvgEventRankingDataList']

        new_index = 10

        # Check if last guild id is at expected location. The last_guild_id should be at idx 10. If not, then
        # we may have hit the end of the list.
        # Find the index of the last guild Id if not at expected location
        while temp_21_list[new_index]['guildDataId'] != last_guild_id:
            print('Not at expected location, incrementing...')
            new_index = new_index + 1


        # Return the list of guilds that come after last_guild_id. Usually 10, but will be less than 10 if there are less than 10 guilds before end the of ranking list
        return temp_21_list[new_index + 1::]