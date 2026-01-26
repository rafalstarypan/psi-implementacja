"""
Management command to seed OAuth2 application.
"""
import os
from django.core.management.base import BaseCommand
from oauth2_provider.models import Application


class Command(BaseCommand):
    help = "Seed OAuth2 application for frontend login"

    def handle(self, *args, **options):
        client_id = os.getenv("OAUTH_CLIENT_ID", "shelter-frontend")

        app, created = Application.objects.get_or_create(
            client_id=client_id,
            defaults={
                "name": "Shelter Frontend",
                "client_type": Application.CLIENT_PUBLIC,
                "authorization_grant_type": Application.GRANT_PASSWORD,
                "skip_authorization": True,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"OAuth app created: {client_id}"))
        else:
            self.stdout.write(self.style.WARNING(f"OAuth app already exists: {client_id}"))
