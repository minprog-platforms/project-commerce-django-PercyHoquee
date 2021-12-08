# Generated by Django 3.2.9 on 2021-12-08 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_listing_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='status',
            field=models.CharField(choices=[('a', 'active'), ('c', 'closed')], default='a', max_length=1),
        ),
    ]