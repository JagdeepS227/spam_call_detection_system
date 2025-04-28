
from django.urls import path

from spam_check.views import ContactListCreateView, SpamReportCreateView, SearchView

urlpatterns = [
    path('contacts/', ContactListCreateView.as_view(), name='create_contact'),
    path('report-spam/', SpamReportCreateView.as_view(), name='report-spam'),
    path('search/', SearchView.as_view(), name='search'),
]
