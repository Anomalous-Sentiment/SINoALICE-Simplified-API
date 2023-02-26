from bs4 import BeautifulSoup
from urllib import request
import re
from datetime import datetime

class NoticesParser():
    BASE_URL = 'https://api-sinoalice-us.pokelabo.jp'
    NOTICES_ENDPOINT = '/web/announce/index?countryCode=36&languageType=2'

    def __init__(self):
        pass

    def get_gc_dates(self):
        gc_dates_dict = None

        try:

            # Get the page html, and parse as soup
            notices_page_soup = BeautifulSoup(request.urlopen(NoticesParser.BASE_URL + NoticesParser.NOTICES_ENDPOINT).read(), 'html.parser')

            # Get the href of the element which links to the Gran Colo notice page
            colo_page_href = self._get_href_with_str(notices_page_soup)

            # Concaternate with base url for full page url
            full_gc_page_url = NoticesParser.BASE_URL + colo_page_href

            # Get the gc notice page html and parse
            colo_page_soup = BeautifulSoup(request.urlopen(full_gc_page_url).read(), 'html.parser')

            # Get the entry dates
            entry_dict = self._get_entry_dates(colo_page_soup)

            # Get the prelim dates
            prelim_dict = self._get_prelim_dates(colo_page_soup)

            # Get the finals dates
            finals_dict = self._get_finals_dates(colo_page_soup)

            # Combine into a single dict
            gc_dates_dict = {}
            gc_dates_dict['entry'] = entry_dict
            gc_dates_dict['prelims'] = prelim_dict
            gc_dates_dict['finals'] = finals_dict

        except PageNotAvailableException:
            print('GC notice page not available')

        # return dict containing all dates. If page not available, return None
        return gc_dates_dict

    def _get_href_with_str(self, soup):
        # Find the string that contains "Colosseum Event: Gran Colosseum Notice"
        colo_string = soup.find(string=re.compile('Colosseum Event: Gran Colosseum Notice'))

        if colo_string is not None:
            # Find the parent <a> element of the string
            a_tag = colo_string.find_parent('a')

            # Get the <a> element href
            href = a_tag['href']
        else:
            raise PageNotAvailableException

        return href

    def _get_prelim_dates(self, colo_page_soup):
        prelim_dict = {}

        # Find the element containing the "Preliminary" text
        prelim_period_header = colo_page_soup.find('p', class_='sub_heading',string=re.compile('Preliminaries'))

        # Move to next sibling element (div containing prelim period)
        prelim_div = prelim_period_header.find_next_sibling('div')

        # Get the 2 spans containing the start and end dates
        date_spans = prelim_div.find_all('span', class_='date-i18n')

        # Get the unix times and parse
        start_date = datetime.utcfromtimestamp(int(date_spans[0]['date-unix-time']))
        end_date = datetime.utcfromtimestamp(int(date_spans[1]['date-unix-time']))

        prelim_dict['start'] = start_date
        prelim_dict['end'] = end_date

        return prelim_dict

    def _get_entry_dates(self, colo_page_soup):
        entry_dict = {}

        # Find the element containing the "Entry Period" text
        entry_period_header = colo_page_soup.find('p', class_='sub_heading',string=re.compile('Entry Period'))

        # Move to next sibling element (div containing entry period)
        entry_div = entry_period_header.find_next_sibling('div')

        # Get the 2 spans containing the start and end dates
        date_spans = entry_div.find_all('span', class_='date-i18n')

        # Get the unix times and parse
        start_date = datetime.utcfromtimestamp(int(date_spans[0]['date-unix-time']))
        end_date = datetime.utcfromtimestamp(int(date_spans[1]['date-unix-time']))

        entry_dict['start'] = start_date
        entry_dict['end'] = end_date

        return entry_dict

    def _get_finals_dates(self, colo_page_soup):
        finals_dict = {}

        # Find the element containing the "Entry Period" text
        finals_period_header = colo_page_soup.find('p', class_='sub_heading',string=re.compile('Finals'))

        # Move to next sibling element (div containing entry period)
        finals_div = finals_period_header.find_next_sibling('div')

        # Get the 2 spans containing the start and end dates
        date_spans = finals_div.find_all('span', class_='date-i18n')

        # Get the unix times and parse
        grp_a_start_date = datetime.utcfromtimestamp(int(date_spans[0]['date-unix-time']))
        grp_a_end_date = datetime.utcfromtimestamp(int(date_spans[1]['date-unix-time']))
        grp_b_start_date = datetime.utcfromtimestamp(int(date_spans[2]['date-unix-time']))
        grp_b_end_date = datetime.utcfromtimestamp(int(date_spans[3]['date-unix-time']))

        finals_dict['grp_a_start'] = grp_a_start_date
        finals_dict['grp_a_end'] = grp_a_end_date
        finals_dict['grp_b_start'] = grp_b_start_date
        finals_dict['grp_b_end'] = grp_b_end_date

        return finals_dict

class PageNotAvailableException(Exception):
    "When gc notice page is not available"