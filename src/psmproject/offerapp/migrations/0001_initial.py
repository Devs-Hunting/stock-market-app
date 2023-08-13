# Generated by Django 4.2.2 on 2023-08-03 18:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Offer",
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
                ("description", models.TextField()),
                ("realization_time", models.DateField()),
                ("budget", models.DecimalField(decimal_places=2, max_digits=6)),
                ("accepted", models.BooleanField(default=False)),
                ("paid", models.BooleanField(default=False)),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "contractor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
