from django.test import TestCase
from django.utils.translation import activate

from trojsten.contests.models import Competition, Round, Series


class RoundMethodTests(TestCase):
    def test_get_pdf_name(self):
        c = Competition.objects.create(name='ABCD')
        s = Series.objects.create(year=47, competition=c, number=1)
        r = Round.objects.create(number=3, series=s, visible=True, solutions_visible=True)
        activate('en')
        self.assertEqual(r.get_pdf_name(), u'ABCD-year47-round3-tasks.pdf')
        self.assertEqual(r.get_pdf_name(True), u'ABCD-year47-round3-solutions.pdf')
        activate('sk')
        self.assertEqual(r.get_pdf_name(), u'ABCD-rocnik47-kolo3-zadania.pdf')
        self.assertEqual(r.get_pdf_name(True), u'ABCD-rocnik47-kolo3-vzoraky.pdf')
