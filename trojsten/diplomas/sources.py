# -*- coding: utf-8 -*-

import re
import json
from abc import abstractmethod
from bs4 import BeautifulSoup

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

from django.template import loader
from django.utils import timezone


class AbstractSource(object):
    name = 'abstract_source'

    def __init__(self):
        pass

    def handle_request(self, request, **kwargs):
        """
        Rendered component on the page is capable of making a request to the backend
        (for cases when obtaining participant data is computationally expensive or they
        are queried from the server). This method provides such interface.

        :param request:
        :param kwargs:
        :return:
        """
        return []

    @abstractmethod
    def render(self, **kwargs):
        """
        Method outputs HTML representation of the source plugin

        :param kwargs:
        :return: Rendered HTML that will be displayed as a component on page
        """
        return ''


class FileUpload(AbstractSource):
    name = 'file_upload'

    def render(self, **kwargs):
        template = loader.get_template('trojsten/diplomas/sources/fileupload.html')
        return template.render()


class Naboj(AbstractSource):
    """
    Base class for Naboj result webpage scraper.
    """

    name = 'naboj'

    @staticmethod
    def compose_url(pattern, *args, **kwargs):
        url_args = []
        for k, v in kwargs.items():
            if v is not None:
                url_args.append('{}={}'.format(k, v))
        url_args = '&'.join(url_args)

        return pattern.format(args=url_args)

    @staticmethod
    def get_latest_year(homepage_url):
        """
        Obtains the current year of the Naboj competition

        :param homepage_url: Url to Naboj index page
        :return: current year of the event if found, otherwise current year in local timezone
        """
        soup = BeautifulSoup(urlopen(homepage_url).read().decode('utf-8'), 'html.parser')
        menu_bar = soup.find('div', id='menucont')
        if not menu_bar:
            return timezone.localdate().year
        item_text = menu_bar.find('a').text
        try:
            return int(item_text.split()[-1])
        except ValueError:
            return timezone.localdate().year

    @staticmethod
    def scrape_results(url, limit=None):
        """
        Scrapes the results of Naboj competition from the given URL.

        :param url: link to result page
        :param limit: maximum number of scraped positions
        :return: JSON-serializable object containing scraped result data
        """
        soup = BeautifulSoup(urlopen(url).read().decode('utf-8'), 'html.parser')

        results_header = soup.find('div', class_='main_content').find('h3').text.split(',')
        results_header = [x.strip() for x in results_header]
        competition, category, location = results_header[0], results_header[1], results_header[2]
        year = competition.split()[-1]

        table = soup.find('table', class_='pretty_table')
        if not table:
            return []
        results = []
        for row in table.find_all('tr')[1:limit + 1 if limit else None]:
            fields = {'rank': row.find('td', class_='col_rank'),
                      'school': row.find('span', class_='results_school'),
                      'address': row.find('span', class_='results_address'),
                      'country': row.find('span', class_='results_country'),
                      'team': row.find('span', class_='results_letter'),
                      'participants': row.find('span', class_='results_participants')}
            row_result = {}
            for k, v in fields.items():
                if v is None:
                    continue
                row_result[k] = v.text

            if 'participants' in row_result:
                participants = [x.strip() for x in row_result['participants'].split(',')]
                for i, p in enumerate(participants):
                    m = re.search(r'(.+) \([0-9]*\)', p.strip())
                    if not m:
                        break

                    participants[i] = m.group(1)
                row_result['participants'] = ', '.join(participants)

            row_result['year'] = year
            row_result['category'] = category
            row_result['location'] = location
            results.append(row_result)

        return results

    def handle_request(self, request, **kwargs):
        request_body = request.body.decode('utf8')
        kwargs.update(json.loads(request_body))
        limit = kwargs.pop('limit', None)
        limit = None if limit == '' else int(limit)
        url = kwargs.pop('url', '')
        url = url if url != '' else self.compose_url(**kwargs)
        return self.scrape_results(url, limit)


class NabojMath(Naboj):

    name = 'naboj_math'

    HOMEPAGE_URL = 'https://math.naboj.org'

    def handle_request(self, request, **kwargs):
        kwargs.update({
            'pattern': '{homepage}/archive/results.php?'.format(homepage=self.HOMEPAGE_URL) + '{args}',
            'year': self.get_latest_year(self.HOMEPAGE_URL),
            'country_code': 'sk'
        })
        return super(NabojMath, self).handle_request(request, **kwargs)

    def render(self, **kwargs):
        context = {
            'categories': [{'name': 'Juniori', 'value': 'jun'}, {'name': 'Seniori', 'value': 'sen'}],
            'name': self.name
        }
        context.update(kwargs)
        template = loader.get_template('trojsten/diplomas/sources/naboj_math.html')
        return template.render(context=context)


class NabojPhysics(NabojMath):

    name = 'naboj_physics'

    HOMEPAGE_URL = 'https://physics.naboj.org'

    def handle_request(self, request, **kwargs):
        kwargs.update({
            'pattern': '{homepage}/archive/results.php?'.format(homepage=self.HOMEPAGE_URL) + '{args}',
            'year': self.get_latest_year(self.HOMEPAGE_URL),
            'country_code': 'sk'
        })
        return super(NabojPhysics, self).handle_request(request, **kwargs)

    def render(self, **kwargs):
        return super(NabojPhysics, self).render(name=self.name)


SOURCE_CHOICES = [
    (FileUpload.name, FileUpload.name),
    (NabojPhysics.name, NabojPhysics.name),
    (NabojMath.name, NabojMath.name)
]

SOURCE_CLASSES = {
    FileUpload.name: FileUpload,
    NabojPhysics.name: NabojPhysics,
    NabojMath.name: NabojMath
}
