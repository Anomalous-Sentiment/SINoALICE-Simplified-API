from bs4 import BeautifulSoup
from urllib import request
import re
from datetime import datetime

class NoticesParser():
    BASE_URL = 'https://api-sinoalice-us.pokelabo.jp'
    NOTICES_ENDPOINT = '/web/announce/index?countryCode=36&languageType=2'

    def __init__():
        pass

    def get_gc_dates(self):
        # Get the page html, and parse as soup
        notices_page_soup = BeautifulSoup(request.urlopen(NoticesParser.BASE_URL + NoticesParser.NOTICES_ENDPOINT).read(), 'html.parser')

        # Get the href of the element which links to the Gran Colo notice page
        colo_page_href = self._get_href_with_str(notices_page_soup)

        # Concaternate with base url for full page url
        full_gc_page_url = NoticesParser.BASE_URL + colo_page_href

        pass

    def _get_href_with_str(self, soup):
        # Find the string that contains "Colosseum Event: Gran Colosseum Notice"
        colo_string = soup.find(string=re.compile('Colosseum Event: Gran Colosseum Notice'))

        # Find the parent <a> element of the string
        a_tag = res.find_parent('a')

        # Get the <a> element href
        href = a_tag['href']

        return href

    def _get_prelim_dates(self):
        pass

    def _get_entry_dates(self):
        pass

    def _get_finals_dates(self):
        pass
