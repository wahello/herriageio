from django.contrib import admin

from .models import (
	BirthdateProfile, 
	BirthdateContactsSegment, BirthdateContact, 
	BirthdateMessageTemplate, BirthdateMessageReminder, BirthdateMessage)


admin.site.register(BirthdateProfile)
admin.site.register(BirthdateContactsSegment)
admin.site.register(BirthdateContact)
admin.site.register(BirthdateMessageTemplate)

class BirthdateMessageTemplateAdmin(admin.ModelAdmin):
    list_select_related = (
        'template',
    )
admin.register(BirthdateMessageTemplate, BirthdateMessageTemplateAdmin)

admin.site.register(BirthdateMessageReminder)
admin.site.register(BirthdateMessage)
