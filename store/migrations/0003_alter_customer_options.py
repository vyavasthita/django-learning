# Generated by Django 4.2.1 on 2023-05-18 09:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_alter_collection_options_alter_product_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'ordering': ['first_name', 'last_name']},
        ),
    ]