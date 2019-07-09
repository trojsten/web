from __future__ import unicode_literals

from django.db import connections

from trojsten.people.management.commands.migrate_base_class import MigrateBaseCommand

# Kaspar property IDs
EMAIL_PROP = 1
BIRTHDAY_PROP = 2


class Command(MigrateBaseCommand):
    help = "Imports people and their related info from kaspar."

    def process_schools(self):
        cursor = self.kaspar.cursor()
        cursor.execute(
            """
            SELECT school_id, short, name, addr_name, addr_street,
                   addr_city, addr_zip
            FROM schools;
        """
        )
        for row in cursor:
            self.process_school(*row)

    def process_particiaptions(self):
        cursor = self.kaspar.cursor()
        cursor.execute(
            """
            SELECT action_id, name, date_start, date_end
            FROM actions
        """
        )

        actions = {}
        for action in cursor:
            actions[action[0]] = {"name": action[1], "start": action[2], "end": action[3]}

        cursor.execute(
            """
            SELECT action_id, man_id, task, note
            FROM participants
        """
        )

        self.camps_survived = {}
        for participant in cursor:
            man_id = participant[1]
            action = actions[participant[0]]
            self.last_contact[man_id].append(int(action["end"].year))
            self.camps_survived[man_id] = self.camps_survived.get(man_id, 0) + 1

    def process_people(self):
        cursor1 = self.kaspar.cursor()
        cursor2 = self.kaspar.cursor()
        fields = ["man_id", "firstname", "lastname", "school_id", "finish", "note"]
        cursor1.execute(
            """
            SELECT %s
            FROM people;
        """
            % (", ".join(fields))
        )

        for l in cursor1:
            l = dict(zip(fields, l))  # noqa: E741
            idcko = l["man_id"]
            self.last_contact[idcko].append(int(l["finish"]) - 3)

            user = {
                "first_name": l["firstname"],
                "last_name": l["lastname"],
                "graduation": l["finish"],
                "school_id": l["school_id"],
            }
            cursor2.execute(
                """
                SELECT ppt_id, value
                FROM people_prop
                WHERE people_prop.man_id = %s AND ppt_id IN (%s, %s);
            """,
                (idcko, EMAIL_PROP, BIRTHDAY_PROP),
            )
            for prop_id, value in cursor2:
                if prop_id == EMAIL_PROP:
                    user["email"] = value
                elif prop_id == BIRTHDAY_PROP:
                    try:
                        user["birth_date"] = self.parse_dot_date(value)
                    except ValueError:
                        # If we can't parse the date, give up.
                        pass

            user_properties = [
                (self.KASPAR_NOTE_PROPERTY, l["note"]),
                (self.KSP_CAMPS_PROPERTY, self.camps_survived.get(idcko, 0)),
            ]
            self.process_person(user, user_properties, self.KASPAR_ID_PROPERTY, idcko)

        cursor1.close()
        cursor2.close()

    def handle(self, **options):
        super(Command, self).handle(**options)
        self.kaspar = connections["kaspar"]

        if self.verbosity >= 1:
            self.stderr.write("Migrating schools...")

        self.process_schools()

        # TODO sustredka

        if self.verbosity >= 1:
            self.stderr.write("Dumping participations")

        self.process_particiaptions()

        if self.verbosity >= 1:
            self.stderr.write("Migrating people...")

        self.process_people()
        self.print_stats()
