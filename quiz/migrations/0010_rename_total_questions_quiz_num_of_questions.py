# Generated by Django 5.0.2 on 2025-06-08 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0009_quiz_total_questions'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quiz',
            old_name='total_questions',
            new_name='num_of_questions',
        ),
    ]
