# Generated by Django 4.2.12 on 2024-05-07 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0002_alter_note_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='created_at',
            field=models.DateTimeField(null=True),
        ),
    ]
