from django.contrib import admin

from spam_check.models import Contact, SpamReport, User

admin.site.register(Contact)
admin.site.register(SpamReport)
admin.site.register(User) 