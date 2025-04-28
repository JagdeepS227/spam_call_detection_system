from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from spam_check.models import User, Contact, SpamReport, PhoneNumberMeta

class CoreAPITest(APITestCase):

    def setUp(self):
        self.password = "Test@123"
        self.user = User.objects.create_user(
            phone_number="8888899999",
            name="Jagdeep Singh",
            password=self.password,
            email="test@example.com"
        )
        self.other_user = User.objects.create_user(
            phone_number="9999988888",
            name="Raman Deep",
            password=self.password
        )
        response = self.client.post(reverse('login'), {
            "phone_number": self.user.phone_number,
            "password": self.password
        })
        self.token = response.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)


    def test_create_contact(self):
        response = self.client.post("/api/contacts/", {
            "name": "Dummy contact",
            "phone_number": self.other_user.phone_number
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_search_by_phone(self):
        SpamReport.objects.create(reporter=self.user, phone_number="8888888888")
        PhoneNumberMeta.objects.update_or_create(
            phone_number="9999988888",
            defaults={"spam_count": 1}
        )
        response = self.client.get("/api/search/?q=9999988888")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['phone_number'], "9999988888")

    def test_search_by_name(self):
        Contact.objects.create(
            owner=self.user,
            name="Cool Friend",
            phone_number="5555544444"
        )
        response = self.client.get("/api/search/?q=cool")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any("Cool" in r["name"] for r in response.data['results']))

    def test_mark_number_as_spam(self):
        number = "5555544444"
        response = self.client.post("/api/report-spam/", {
            "phone_number": number
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        phone_num = PhoneNumberMeta.objects.get(phone_number=number)
        self.assertEqual(phone_num.spam_count, 1)

