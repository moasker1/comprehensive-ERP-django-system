# Generated by Django 3.2.23 on 2024-01-02 18:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplier',
            name='date_created',
            field=models.DateField(default=datetime.date(2024, 1, 2)),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='place',
            field=models.CharField(default='غير محدد', max_length=70),
        ),
    ]
