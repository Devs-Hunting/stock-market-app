# Generated by Django 4.2.3 on 2023-08-09 20:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chatapp", "0002_participant_unique_user_in_chat"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="content",
            field=models.CharField(max_length=500),
        ),
    ]
