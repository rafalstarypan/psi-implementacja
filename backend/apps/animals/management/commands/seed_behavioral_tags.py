
from django.core.management.base import BaseCommand
from apps.animals.models import  BehavioralTag


class Command(BaseCommand):
    help = 'Seed behavioral tags data'

    def handle(self, *args, **options):
        self.seed_tags()
        self.stdout.write(self.style.SUCCESS('Behavioral tags data seeding completed!'))

    def seed_tags(self):
        tags_data = [
            {
                'beahavioral_tag_name': 'calm',
                'description': 'The animal is calm and well-behaved.'
            },
            {
                'beahavioral_tag_name': 'aggressive',
                'description': 'The animal is aggressive and needs careful handling.'
            },
            {
                'beahavioral_tag_name': 'shy',
                'description': 'The animal is shy and needs gentle approach.'
            },
            {
                'beahavioral_tag_name': 'playful',
                'description': 'The animal is playful and enjoys interaction.'
            },
        ]

        for data in tags_data:
            behavioral_tag_name = data.pop('beahavioral_tag_name')
            behavioral_tag, created = BehavioralTag.objects.get_or_create(
                behavioral_tag_name=behavioral_tag_name,
                defaults=data
            )
            if created:
                self.stdout.write(f'Created behavioral tag: {behavioral_tag.behavioral_tag_name}')
            else:
                self.stdout.write(self.style.WARNING(f'Behavioral tag already exists: {behavioral_tag.behavioral_tag_name}'))


