# Generated by Django 2.1 on 2018-08-16 06:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('substitute_finder', '0004_auto_20180815_0204'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='categories',
            new_name='categories_tags',
        ),
    ]