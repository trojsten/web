# -*- coding: utf-8 -*-

import sys
from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve
from django.template import loader
from django.utils import timezone
import re
import json

class Source:
    @staticmethod
    def handle_request(request):
        pass

    @staticmethod
    def render():
        return ""


class FileUpload:
    @staticmethod
    def render():
        template = loader.get_template('trojsten/diplomas/parts/fileupload.html')
        return template.render()


class Naboj:

    @staticmethod
    def compose_url(pattern, *args, **kwargs):
        url_args = []
        for k, v in kwargs.items():
            if v is not None:
                url_args.append("{}={}".format(k, v))
        url_args = "&".join(url_args)

        return pattern.format(args=url_args)

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

    @staticmethod
    def handle_request(request):
        request_body = request.body.decode('utf8')
        kwargs = json.loads(request_body)
        limit = kwargs.pop('limit', None)
        limit = None if limit == '' else int(limit)
        kwargs.update({
            'pattern': "https://math.naboj.org/archive/results.php?{args}",
            'year': timezone.localdate().year,
            'country_code': 'sk'
        })
        url = Naboj.compose_url(**kwargs)
        return Naboj.scrape_results(url, limit)

    @staticmethod
    def render():
        ctx = {
            'category': {'categories': [{'name': 'Juniori', 'value': 'jun'}, {'name': 'Seniori', 'value': 'sen'}],
                         'label': 'Kategórie'},
            'source_class': 'Naboj'
        }
        template = loader.get_template('trojsten/diplomas/parts/naboj.html')
        return template.render(context=ctx)


class TrojstenResults:

    @staticmethod
    def render():
        template = loader.get_template('trojsten/diplomas/parts/trojstenresults.html')
        return template.render()


def get_class(name):
    return getattr(sys.modules[__name__], name, None)
