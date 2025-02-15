from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates test users for the trading platform'

    def handle(self, *args, **kwargs):
        test_users = [
            {'username': 'trader1', 'password': 'test1234', 'email': 'trader1@test.com'},
            {'username': 'trader2', 'password': 'test1234', 'email': 'trader2@test.com'},
            {'username': 'trader3', 'password': 'test1234', 'email': 'trader3@test.com'},
        ]

        for user_data in test_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                email=user_data['email']
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Created user: {user.username}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'User already exists: {user.username}')
                )