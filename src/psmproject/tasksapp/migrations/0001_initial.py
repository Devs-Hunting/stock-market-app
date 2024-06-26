# Generated by Django 4.2.10 on 2024-05-07 20:52

import django.core.validators
import django.db.models.deletion
import tasksapp.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("usersapp", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Complaint",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("content", models.TextField()),
                ("closed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "arbiter",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="complaints_to_judge",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "complainant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="complaints_made",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Offer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("description", models.TextField(verbose_name="description")),
                (
                    "days_to_complete",
                    models.PositiveIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)], verbose_name="days to complete"
                    ),
                ),
                ("realization_time", models.DateField(blank=True, null=True, verbose_name="realization time")),
                ("budget", models.DecimalField(decimal_places=2, max_digits=8, verbose_name="budget")),
                ("accepted", models.BooleanField(default=False, verbose_name="accepted")),
                ("created", models.DateTimeField(auto_now_add=True, verbose_name="created")),
                (
                    "contractor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="contractor",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=8)),
                (
                    "fee_percentage",
                    models.PositiveIntegerField(default=15, validators=[django.core.validators.MaxValueValidator(15)]),
                ),
                (
                    "advance_percentage",
                    models.PositiveIntegerField(default=50, validators=[django.core.validators.MaxValueValidator(100)]),
                ),
                ("advance_received", models.BooleanField(default=False)),
                ("total_amount_received", models.BooleanField(default=False)),
                ("contractor_paid", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Solution",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("description", models.TextField()),
                ("submitted", models.BooleanField(default=True)),
                ("accepted", models.BooleanField(default=False)),
                ("end", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=120, verbose_name="title")),
                ("description", models.TextField(verbose_name="description")),
                (
                    "days_to_complete",
                    models.PositiveIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)], verbose_name="days to complete"
                    ),
                ),
                ("budget", models.DecimalField(decimal_places=2, max_digits=8, verbose_name="budget")),
                (
                    "status",
                    models.IntegerField(
                        choices=[
                            (0, "open"),
                            (1, "on-hold"),
                            (2, "on-going"),
                            (3, "objections"),
                            (4, "completed"),
                            (5, "cancelled"),
                        ],
                        default=0,
                        verbose_name="status",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, verbose_name="created")),
                ("updated", models.DateTimeField(auto_now=True, verbose_name="updated")),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name="client"
                    ),
                ),
                (
                    "selected_offer",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="in_task",
                        to="tasksapp.offer",
                        verbose_name="selected offer",
                    ),
                ),
                ("skills", models.ManyToManyField(to="usersapp.skill", verbose_name="skills")),
            ],
        ),
        migrations.CreateModel(
            name="TaskAttachment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("attachment", models.FileField(upload_to=tasksapp.models.get_upload_path, verbose_name="attachment")),
                ("created", models.DateTimeField(auto_now_add=True, verbose_name="created")),
                ("updated", models.DateTimeField(auto_now=True, verbose_name="updated")),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="tasksapp.task",
                        verbose_name="task",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SolutionAttachment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("attachment", models.FileField(upload_to=tasksapp.models.get_upload_path, verbose_name="attachment")),
                ("created", models.DateTimeField(auto_now_add=True, verbose_name="created")),
                ("updated", models.DateTimeField(auto_now=True, verbose_name="updated")),
                (
                    "solution",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="tasksapp.solution",
                        verbose_name="solution",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="offer",
            name="payment",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="offer",
                to="tasksapp.payment",
                verbose_name="payment",
            ),
        ),
        migrations.AddField(
            model_name="offer",
            name="solution",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="offer",
                to="tasksapp.solution",
                verbose_name="solution",
            ),
        ),
        migrations.AddField(
            model_name="offer",
            name="task",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="offers",
                to="tasksapp.task",
                verbose_name="task",
            ),
        ),
        migrations.CreateModel(
            name="ComplaintAttachment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("attachment", models.FileField(upload_to=tasksapp.models.get_upload_path, verbose_name="attachment")),
                ("created", models.DateTimeField(auto_now_add=True, verbose_name="created")),
                ("updated", models.DateTimeField(auto_now=True, verbose_name="updated")),
                (
                    "complaint",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="tasksapp.complaint",
                        verbose_name="complaint",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="complaint",
            name="task",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="complaints", to="tasksapp.task"
            ),
        ),
        migrations.AddConstraint(
            model_name="complaint",
            constraint=models.UniqueConstraint(
                fields=("task", "complainant"),
                name="unique_task_user",
                violation_error_message="cannot create second complaint for this task",
            ),
        ),
    ]
