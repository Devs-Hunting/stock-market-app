# Generated by Django 4.2.4 on 2023-09-14 19:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("offerapp", "0001_initial"),
        ("tasksapp", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="offer",
            name="task",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, related_name="task", to="tasksapp.task"
            ),
        ),
        migrations.AddField(
            model_name="complaintattachment",
            name="complaint",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attachment",
                to="offerapp.complaint",
            ),
        ),
        migrations.AddField(
            model_name="complaint",
            name="arbiter",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
