from django.core.management.base import BaseCommand
from quiz.models import Subject

class Command(BaseCommand):
    help = 'Create initial WASSCE subjects'

    def handle(self, *args, **options):
        subjects = [
            "Mathematics",
            "English Language",
            "Physics",
            "Chemistry",
            "Biology",
            "Economics",
            "Geography",
            "Literature",
            "History"
        ]
        
        created_count = 0
        existing_count = 0
        
        for subject_name in subjects:
            subject, created = Subject.objects.get_or_create(name=subject_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created subject: {subject_name}'))
                created_count += 1
            else:
                self.stdout.write(self.style.WARNING(f'Subject already exists: {subject_name}'))
                existing_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\nCreated {created_count} new subjects'))
        if existing_count:
            self.stdout.write(self.style.WARNING(f'{existing_count} subjects already existed')) 