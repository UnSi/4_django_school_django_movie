# Generated by Django 3.0.6 on 2020-06-08 16:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0003_auto_20200608_1932'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='world_premiere',
            field=models.DateField(default=datetime.date.today, verbose_name='Премьера в мире'),
        ),
    ]