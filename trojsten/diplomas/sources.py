# -*- coding: utf-8 -*-
#from __future__ import unicode_literals

from bs4 import BeautifulSoup
from urllib.request import urlopen
from django.template import loader
from django.utils import timezone
import re
import json
from abc import abstractmethod


class AbstractSource(object):
    name = 'abstract_source'

    def __init__(self):
        pass

    def handle_request(self, request, **kwargs):
        return []

    @abstractmethod
    def render(self, **kwargs):
        return ""


class FileUpload(AbstractSource):
    name = 'file_upload'

    def render(self, **kwargs):
        template = loader.get_template('trojsten/diplomas/parts/fileupload.html')
        return template.render()


class Naboj(AbstractSource):

    name = 'naboj'

    @staticmethod
    def compose_url(pattern, *args, **kwargs):
        url_args = []
        for k, v in kwargs.items():
            if v is not None:
                url_args.append("{}={}".format(k, v))
        url_args = "&".join(url_args)

        return pattern.format(args=url_args)

    @staticmethod
    def get_latest_year(homepage):
        soup = BeautifulSoup(urlopen(homepage).read().decode("utf-8"), 'html.parser')
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
        soup = BeautifulSoup(urlopen(url).read().decode("utf-8"), 'html.parser')
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
                row_result['participants'] = ", ".join(participants)
            results.append(row_result)

        return results

    def handle_request(self, request, **kwargs):
        request_body = request.body.decode('utf8')
        kwargs.update(json.loads(request_body))
        limit = kwargs.pop('limit', None)
        limit = None if limit == '' else int(limit)
        url = self.compose_url(**kwargs)
        return self.scrape_results(url, limit)


class NabojMath(Naboj):

    name = 'naboj_math'

    HOMEPAGE_URL = 'https://math.naboj.org'

    def handle_request(self, request, **kwargs):
        kwargs.update({
            'pattern': "{homepage}/archive/results.php?".format(homepage=self.HOMEPAGE_URL) + '{args}',
            'year': self.get_latest_year(self.HOMEPAGE_URL),
            'country_code': 'sk'
        })
        return super(NabojMath, self).handle_request(request, **kwargs)

    def render(self, **kwargs):
        context = {
            'category': {'categories': [{'name': 'Juniori', 'value': 'jun'}, {'name': 'Seniori', 'value': 'sen'}],
                         'label': 'Kategórie'},
            'name': self.name
        }
        context.update(kwargs)
        template = loader.get_template('trojsten/diplomas/parts/naboj_math.html')
        return template.render(context=context)


class NabojPhysics(NabojMath):

    name = 'naboj_physics'

    HOMEPAGE_URL = 'https://physics.naboj.org'

    def handle_request(self, request, **kwargs):
        kwargs.update({
            'pattern': "{homepage}/archive/results.php?".format(homepage=self.HOMEPAGE_URL) + '{args}',
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
