# Generated by Django 4.2.2 on 2023-06-22 13:03


import django.db.models.deletion
import tasksapp.models
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=120)),
                ("description", models.TextField()),
                ("realization_time", models.DateField()),
                ("budget", models.DecimalField(decimal_places=2, max_digits=6)),
                (
                    "status",
                    models.IntegerField(
                        choices=[
                            (0, "open"),
                            (1, "closed"),
                            (2, "on-going"),
                            (3, "objections"),
                            (4, "completed"),
                            (5, "cancelled"),
                        ],
                        default=0,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="TaskAttachment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "attachment",
                    models.FileField(upload_to=tasksapp.models.get_upload_path),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="tasksapp.task",
                    ),
                ),
            ],
        ),
    ]
