# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.utils.timezone
import trojsten.regal.people.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('gender', models.CharField(default='M', max_length=1, verbose_name='pohlavie', choices=[('M', 'Chlapec'), ('F', 'Diev\u010da')])),
                ('birth_date', models.DateField(null=True, verbose_name='d\xe1tum narodenia', db_index=True)),
                ('graduation', models.IntegerField(help_text='Povinn\xe9 pre \u017eiakov.', null=True, verbose_name='rok maturity')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
            ],
            options={
                'verbose_name': 'pou\u017e\xedvate\u013e',
                'verbose_name_plural': 'pou\u017e\xedvatelia',
            },
            managers=[
                ('objects', trojsten.regal.people.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('street', models.CharField(max_length=70, verbose_name='ulica')),
                ('town', models.CharField(max_length=64, verbose_name='mesto', db_index=True)),
                ('postal_code', models.CharField(max_length=16, verbose_name='PS\u010c', db_index=True)),
                ('country', models.CharField(max_length=32, verbose_name='krajina', db_index=True)),
            ],
            options={
                'verbose_name': 'Adresa',
                'verbose_name_plural': 'Adresy',
            },
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('abbreviation', models.CharField(help_text='Sktatka n\xe1zvu \u0161koly.', max_length=100, verbose_name='skratka', blank=True)),
                ('verbose_name', models.CharField(max_length=100, verbose_name='cel\xfd n\xe1zov')),
                ('addr_name', models.CharField(max_length=100, verbose_name='n\xe1zov v adrese', blank=True)),
                ('street', models.CharField(max_length=100, verbose_name='ulica', blank=True)),
                ('city', models.CharField(max_length=100, verbose_name='mesto', blank=True)),
                ('zip_code', models.CharField(max_length=10, verbose_name='PS\u010c', blank=True)),
            ],
            options={
                'ordering': ('city', 'street', 'verbose_name'),
                'verbose_name': '\u0161kola',
                'verbose_name_plural': '\u0161koly',
            },
        ),
        migrations.CreateModel(
            name='UserProperty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField(verbose_name='hodnota vlastnosti')),
            ],
            options={
                'verbose_name': 'dodato\u010dn\xe1 vlastnos\u0165',
                'verbose_name_plural': 'dodato\u010dn\xe9 vlastnosti',
            },
        ),
        migrations.CreateModel(
            name='UserPropertyKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key_name', models.CharField(max_length=100, verbose_name='n\xe1zov vlastnosti')),
            ],
            options={
                'verbose_name': 'k\u013e\xfa\u010d dodato\u010dnej vlastnosti',
                'verbose_name_plural': 'k\u013e\xfa\u010de dodato\u010dnej vlastnosti',
            },
        ),
        migrations.AddField(
            model_name='userproperty',
            name='key',
            field=models.ForeignKey(related_name='properties', verbose_name='n\xe1zov vlastnosti', to='people.UserPropertyKey'),
        ),
        migrations.AddField(
            model_name='userproperty',
            name='user',
            field=models.ForeignKey(related_name='properties', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='home_address',
            field=models.ForeignKey(related_name='lives_here', verbose_name='dom\xe1ca adresa', to='people.Address', null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='mailing_address',
            field=models.ForeignKey(related_name='accepting_mails_here', verbose_name='adresa kore\u0161pondencie', blank=True, to='people.Address', null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='school',
            field=models.ForeignKey(default=1, to='people.School', help_text='Do pol\xed\u010dka nap\xed\u0161te skratku, \u010das\u0165 n\xe1zvu alebo adresy \u0161koly a n\xe1sledne vyberte spr\xe1vnu mo\u017enos\u0165 zo zoznamu. Pokia\u013e va\u0161a \u0161kola nie je v&nbsp;zozname, vyberte "Gymn\xe1zium in\xe9" a&nbsp;po\u0161lite n\xe1m e-mail.', null=True, verbose_name='\u0161kola'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='userproperty',
            unique_together=set([('user', 'key')]),
        ),
    ]
