from __future__ import unicode_literals

from django.db import connections
from trojsten.people.management.commands.migrate_base_class import MigrateBaceCommand

# Kaspar property IDs
EMAIL_PROP = 1
BIRTHDAY_PROP = 2


class Command(MigrateBaceCommand):
    help = 'Imports people and their related info from kaspar.'

    def handle_noargs(self, **options):
        super(Command, self).handle_noargs(**options)
        kaspar = connections['kaspar']

        if self.verbosity >= 1:
            self.stdout.write("Migrating schools...")

        c = kaspar.cursor()
        c.execute("""
            SELECT school_id, short, name, addr_name, addr_street,
                   addr_city, addr_zip
            FROM schools;
        """)
        self.school_id_map = dict()
        for row in c:
            self.process_school(*row)

        # TODO sustredka

        if self.verbosity >= 1:
            self.stdout.write("Dumping participations")

        c.execute("""
            SELECT action_id, name, date_start, date_end
            FROM actions
        """)

        actions = {}
        for action in c:
            actions[action[0]] = {
                "name": action[1],
                "start": action[2],
                "end": action[3]
            }

        c.execute("""
            SELECT action_id, man_id, task, note
            FROM participants
        """)

        camps_survived = {}
        for participant in c:
            man_id = participant[1]
            action = actions[participant[0]]
            self.last_contact[man_id].append(int(action['end'].year))
            camps_survived[man_id] = camps_survived.get(man_id, 0) + 1

        if self.verbosity >= 1:
            self.stdout.write("Creating/retrieving required UserPropertyKeys...")

        if self.verbosity >= 1:
            self.stdout.write("Migrating people...")

        fields = ["man_id", "firstname", "lastname", "school_id", "finish", "note"]
        c.execute("""
            SELECT %s
            FROM people;
        """ % (', '.join(fields)))

        for l in c:
            l = dict(zip(fields, l))
            idcko = l['man_id']
            self.last_contact[idcko].append(int(l['finish'])-3)

            user = {
                'first_name': l['firstname'],
                'last_name': l['lastname'],
                'graduation': l['finish'],
                'school_id': l['school_id']
            }
            cc = kaspar.cursor()
            cc.execute("""
                SELECT ppt_id, value
                FROM people_prop
                WHERE people_prop.man_id = %s AND ppt_id IN (%s, %s);
            """, (idcko, EMAIL_PROP, BIRTHDAY_PROP))
            for prop_id, value in cc:
                if prop_id == EMAIL_PROP:
                    user['email'] = value
                elif prop_id == BIRTHDAY_PROP:
                    try:
                        user['birth_date'] = self.parse_dot_date(value)
                    except ValueError:
                        # If we can't parse the date, give up.
                        pass
            cc.close()

            user_properties = [
                (self.KASPAR_NOTE_PROPERTY, l['note']),
                (self.KSP_CAMPS_PROPERTY, camps_survived.get(idcko, 0))
            ]
            self.process_person(user, user_properties, self.KASPAR_ID_PROPERTY, idcko)

        self.print_stats()
