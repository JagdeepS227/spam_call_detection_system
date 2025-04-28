from django.contrib.auth import get_user_model

from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from spam_check.constants import PHONE_NUMBER_LENGTH
from spam_check.models import Contact, SpamReport, PhoneNumberMeta
from spam_check.serializers import ContactSerializer, SpamReportSerializer
from rest_framework.throttling import UserRateThrottle
User = get_user_model()

class ContactListCreateView(generics.ListCreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



class SpamReportCreateView(generics.CreateAPIView):
    serializer_class = SpamReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)


def get_spam_score(report_count):
    if report_count == 0:
        return "Not spam"
    elif report_count <= 2:
        return "Low"
    elif report_count <= 5:
        return "Medium"
    else:
        return "High"



class SearchRateThrottle(UserRateThrottle):
    scope = 'search'

class SearchView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [SearchRateThrottle]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        results = []
        seen = set()

        is_phone = query.isdigit() and len(query) == PHONE_NUMBER_LENGTH

        def get_spam_count(phone):
            return PhoneNumberMeta.objects.filter(phone_number=phone).values_list('spam_count', flat=True).first() or 0

        if is_phone:
            phone = query
            spam_count = get_spam_count(phone)

            try:
                user = User.objects.get(phone_number=phone)
                email = None
                if Contact.objects.filter(owner=user, phone_number=request.user.phone_number).exists():
                    email = user.email

                results.append({
                    "name": user.name,
                    "phone_number": user.phone_number,
                    "email": email,
                    "spam_count": spam_count,
                    "spam_likelihood":get_spam_score(spam_count)
                })
                return Response(results)

            except User.DoesNotExist:
                pass

            contacts = Contact.objects.filter(phone_number=phone)
            for contact in contacts:
                key = (contact.name, contact.phone_number)
                if key not in seen:
                    results.append({
                        "name": contact.name,
                        "phone_number": contact.phone_number,
                        "email": None,
                        "spam_count": spam_count,
                        "spam_likelihood":get_spam_score(spam_count)
                    })
                    seen.add(key)

            if not results and SpamReport.objects.filter(phone_number=phone).exists():
                results.append({
                    "name": None,
                    "phone_number": phone,
                    "email": None,
                    "spam_count": spam_count,
                    "spam_likelihood":get_spam_score(spam_count)
                })

        else:#if input comes as a name
            query = query.lower()#casing shouldn't be considered
            users = User.objects.filter(name__icontains=query)
            for user in users:
                key = (user.name, user.phone_number)
                if key in seen:
                    continue

                email = None
                print(request.user.phone_number, "checkq", user)
                if Contact.objects.filter(owner=user, phone_number=request.user.phone_number).exists():
                    print("reaching this point")
                    email = user.email

                results.append({
                    "name": user.name,
                    "phone_number": user.phone_number,
                    "email": email,
                    "spam_count": get_spam_count(user.phone_number),
                    "spam_likelihood":get_spam_score(get_spam_count(user.phone_number))
                })
                seen.add(key)

            contacts = Contact.objects.filter(name__icontains=query)
            for contact in contacts:
                key = (contact.name, contact.phone_number)
                if key in seen:
                    continue

                results.append({
                    "name": contact.name,
                    "phone_number": contact.phone_number,
                    "email": None,
                    "spam_count": get_spam_count(contact.phone_number),
                    "spam_likelihood":get_spam_score(get_spam_count(contact.phone_number))
                })
                seen.add(key)
            results.sort(key=lambda x: (not x['name'] or not x['name'].lower().startswith(query), x['name'] or ''))
        if not results:
            return Response(
                {"detail": "No matching results found."},
                status=status.HTTP_404_NOT_FOUND
            )
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(results, request)
        return paginator.get_paginated_response(page)