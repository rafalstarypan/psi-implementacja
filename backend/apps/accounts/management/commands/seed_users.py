"""
Management command to seed test users.
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User, Role


class Command(BaseCommand):
    help = 'Seed test users for demonstration purposes'

    def handle(self, *args, **options):
        # Create superuser for Django Admin
        admin_email = 'admin@schronisko.pl'
        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_superuser(
                email=admin_email,
                password='admin123',
                first_name='Admin',
                last_name='Systemu',
                role=Role.EMPLOYEE,
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created superuser: {admin_email}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Superuser already exists: {admin_email}')
            )

        users_data = [
            {
                'email': 'pracownik@schronisko.pl',
                'password': 'haslo123',
                'first_name': 'Jan',
                'last_name': 'Kowalski',
                'role': Role.EMPLOYEE,
            },
            {
                'email': 'wolontariusz@schronisko.pl',
                'password': 'haslo123',
                'first_name': 'Anna',
                'last_name': 'Nowak',
                'role': Role.VOLUNTEER,
            },
            {
                'email': 'odwiedzajacy@schronisko.pl',
                'password': 'haslo123',
                'first_name': 'Piotr',
                'last_name': 'Wiśniewski',
                'role': Role.VISITOR,
            },
            # Additional veterinarians (employees) for medical records
            {
                'email': 'dr.kowalczyk@schronisko.pl',
                'password': 'haslo123',
                'first_name': 'Maria',
                'last_name': 'Kowalczyk',
                'role': Role.EMPLOYEE,
            },
            {
                'email': 'dr.zielinski@schronisko.pl',
                'password': 'haslo123',
                'first_name': 'Tomasz',
                'last_name': 'Zieliński',
                'role': Role.EMPLOYEE,
            },
        ]

        for user_data in users_data:
            email = user_data.pop('email')
            password = user_data.pop('password')

            user, created = User.objects.get_or_create(
                email=email,
                defaults=user_data
            )

            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Created user: {email} ({user.get_role_display()})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'User already exists: {email}')
                )

        self.stdout.write(self.style.SUCCESS('User seeding completed!'))
