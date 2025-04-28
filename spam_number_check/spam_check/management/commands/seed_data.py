from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from spam_check.models import Contact, SpamReport, PhoneNumberMeta
from faker import Faker
import random
import os
fake = Faker()
User = get_user_model()
NUM_USERS = 50
MAX_CONTACTS_PER_USER = 10
MAX_SPAM_REPORTS = 100
NUM_SPAM_ONLY_NUMBERS = 20

class Command(BaseCommand):
    help = "Seed the database with fake users, contacts, spam reports, and logs data to a file."

    def handle(self, *args, **kwargs):
        log_path = os.path.join("Data_writing_logs.txt")
        log_file = open(log_path, "w")
        self.stdout.write("Seeding data...")
        log_file.write("|*|*|*|*|*|*| Seeding Logs |*|*|*|*|*|*|\n")
        users = []
        for _ in range(NUM_USERS):
            phone = fake.unique.msisdn()[-10:]
            name = fake.name()
            user = User.objects.create_user(
                phone_number=phone,
                name=name,
                password="Test@123"
            )
            if random.random() < 0.5:
                user.email = fake.email()
                user.save()
            users.append(user)
            log_file.write(f"User: {name} | {phone} | Email: {user.email} | Password: 'Test@123'\n")
        self.stdout.write(f"Created {len(users)} users.")
        contacts_created = 0
        for user in users:
            other_users = [u for u in users if u != user]
            for _ in range(random.randint(1, MAX_CONTACTS_PER_USER)):
                target = random.choice(other_users)
                contact_name = fake.name()
                if not Contact.objects.filter(owner=user, phone_number=target.phone_number).exists():
                    contact = Contact.objects.create(
                        owner=user,
                        phone_number=target.phone_number,
                        name=contact_name
                    )
                    log_file.write(f"Contact for {user.phone_number}: {contact_name} ({target.phone_number})\n")
                    contacts_created += 1

        self.stdout.write(f"Created {contacts_created} contacts.")
        spam_reports = 0
        for _ in range(MAX_SPAM_REPORTS):
            reporter = random.choice(users)
            target = random.choice(users + [None])

            if target:
                number = target.phone_number
            else:
                number = fake.unique.msisdn()[-10:]

            if not SpamReport.objects.filter(reporter=reporter, phone_number=number).exists():
                SpamReport.objects.create(reporter=reporter, phone_number=number)
                obj, _ = PhoneNumberMeta.objects.get_or_create(phone_number=number)
                obj.spam_count += 1
                obj.save()
                log_file.write(f"Spam Report: {reporter.phone_number} ➝ {number}\n")
                spam_reports += 1
        self.stdout.write(f"Created {spam_reports} spam reports.")

        for _ in range(NUM_SPAM_ONLY_NUMBERS):
            phone = fake.unique.msisdn()[-10:]
            report_count = random.randint(1, 10)

            for _ in range(report_count):
                reporter = random.choice(users)
                if not SpamReport.objects.filter(reporter=reporter, phone_number=phone).exists():
                    SpamReport.objects.create(reporter=reporter, phone_number=phone)
                    obj, _ = PhoneNumberMeta.objects.get_or_create(phone_number=phone)
                    obj.spam_count += 1
                    obj.save()
                    log_file.write(f"Spam-only Report: {reporter.phone_number} ➝ {phone}\n")
        self.stdout.write(f"Created {NUM_SPAM_ONLY_NUMBERS} spam-only numbers.")
        log_file.write("|*|*|*|*|*|*| Done |*|*|*|*|*|*|\n")
        log_file.close()
        self.stdout.write(self.style.SUCCESS(f"Done seeding all data. Logs saved to {log_path}"))
