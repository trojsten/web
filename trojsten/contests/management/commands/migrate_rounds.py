# coding: utf-8

import csv
import re

import pytz
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from trojsten.contests.models import Competition, Round, Semester


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("fname", help="CSV file with rounds.")

    def handle(self, *args, **options):
        fname = options["fname"]

        semester_re = re.compile(
            r"(?P<semester_number>\d+)\. \((?P<semester_name>.*)\) časť, (?P<year>\d+)\. ročník (?P<competition>.*)"
        )

        date_re = re.compile(r"(?P<day>\d{1,2})\.(?P<month>\d{1,2})\.(?P<year>\d{4})")

        time_re = re.compile(r"(?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2})")

        def get_or_create_semester(semester):
            """Parses string like: '1. (Zimná) časť, 9. ročník FKS' and createws semester out of it."""
            parsed_semester = semester_re.match(semester).groupdict()
            competition = Competition.objects.get(name=parsed_semester["competition"])
            semester, created = Semester.objects.get_or_create(
                competition=competition,
                name=parsed_semester["semester_name"],
                number=int(parsed_semester["semester_number"]),
                year=int(parsed_semester["year"]),
            )
            if created:
                print("Created new semester {}".format(semester))
            return semester

        def parse_time(date, time):
            parsed_date = date_re.match(date).groupdict()
            parsed_time = time_re.match(time).groupdict()
            return timezone.make_aware(
                timezone.datetime(
                    year=int(parsed_date["year"]),
                    month=int(parsed_date["month"]),
                    day=int(parsed_date["day"]),
                    hour=int(parsed_time["hour"]),
                    minute=int(parsed_time["minute"]),
                    second=int(parsed_time["second"]),
                )
            )

        def parse_bool(val):
            return val == "TRUE"

        with open(fname, newline="") as f:
            round_reader = csv.reader(f)
            for i, row in enumerate(round_reader):
                if i > 0:
                    semester = get_or_create_semester(row[0])
                    number = int(row[1])
                    start_time = parse_time(date=row[2], time=row[3])
                    end_time = parse_time(date=row[4], time=row[5])
                    visible = parse_bool(row[6])
                    solutions_visible = parse_bool(row[7])
                    results_final = parse_bool(row[8])

                    round, created = Round.objects.get_or_create(
                        semester=semester,
                        number=number,
                        start_time=start_time,
                        end_time=end_time,
                        visible=visible,
                        solutions_visible=solutions_visible,
                        results_final=results_final,
                    )
                    if created:
                        print("Created new round: {} (row: {})".format(round, i))
                    else:
                        print("Skipping round: {} (row: {})".format(round, i))
