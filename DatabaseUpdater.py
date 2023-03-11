from api.GuildAPI import GuildAPI
from api.PlayerAPI import PlayerAPI
from api.GranColoAPI import GranColoAPI
from api.NoticesParser import NoticesParser
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.dialects.postgresql import insert
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, date, timedelta
from apscheduler.schedulers.background import BlockingScheduler

class DatabaseUpdater():
    def __init__(self):
        self.job_list = []
        self.sched = BlockingScheduler()
        
    def run(self):
        # Shedule to run the update task every day, 5 min after reset
        shed.add_job(self._daily_update, 'cron', hour=5, minute=5)
        sched.start()

    def _update_guilds(self):
        pass

    def _update_players(self, guild_list):
        pass

    def _update_gc_ranks(self, gc_num, day, timeslot):
        pass

    def _daily_update(self):
        guild_api = GuildAPI()
        player_api = PlayerAPI()
        notices_parser = NoticesParser()

        # Update the guilds

        # Update the players using guild list

        # Check if GC dates available
        gc_dates = notices_parser.get_gc_dates()

        if gc_dates != None:
            # Check if today is before prelim date
            if datetime.today() < gc_dates['prelims']['start']:
                # Run the function to schedule gc ranking updates
                self._schedule_gc_updates(gc_dates['prelims']['start'], gc_dates['prelims']['end'])

    def _schedule_gc_updates(self, start_date, end_date):
        # The time slot number, and the hours offset from reset time
        colo_time_offsets = [
            (3, timedelta(hours=14)),
            (4, timedelta(hours=15)),
            (5, timedelta(hours=16)),
            (6, timedelta(hours=18)),
            (7, timedelta(hours=20)),
            (8, timedelta(hours=21)),
            (9, timedelta(hours=22)),
            (10, timedelta(hours=23)),
            (12, timedelta(hours=8)),
            (13, timedelta(hours=9)),
        ]

        # Remove all previously scheduled gc updates
        for job in self.job_list:
            job.remove()

        # Use the first month of gc to calculate the current GC number
        # This assumes that a GC occurs every month, and only once every month. This will become inaccurate otherwise
        first_gc_month = datetime(2020, 8, 1)
        curr_gc = ((start_date.year - first_gc_month.year) * 12 + start_date.month - first_gc_month.month) + 1

        print(curr_gc)

        # Calculate number of days in prelims (In case it ever changes, though I doubt it will)
        # The 1 second timedelta is because the end datetime is 1 sec short of being a full 6 days right now
        prelim_days = (end_date - start_date + timedelta(seconds=1)).days

        # Schedule an update of the gc ranks after every time slot's colo
        for day in range(prelim_days):
            for timeslot, offset in colo_time_offsets:
                print('timeslot: ' + str(timeslot) + ', day: ' + str(day))
                update_datetime = start_date + timedelta(days=day) + offset
                print(update_datetime)
                # Schedule update job and add to list
                new_job = self.sched.add_job(self._update_gc_ranks, run_date=update_datetime, args=[curr_gc, day + 1, timeslot])
                self.job_list.append(new_job)
