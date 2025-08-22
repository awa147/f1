from django.contrib import admin
from .models import EventCategory, CampusEvent, EventRegistration, BookmarkedEvent

@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_count')
    search_fields = ('name',)
    
    def event_count(self, obj):
        return obj.campusevent_set.count()
    event_count.short_description = '活动数量'

@admin.register(CampusEvent)
class CampusEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'start_time', 'end_time', 'status', 'registration_count')
    list_filter = ('status', 'category', 'is_featured')
    search_fields = ('title', 'description', 'location')
    filter_horizontal = ()
    date_hierarchy = 'start_time'
    
    def registration_count(self, obj):
        return obj.registrations.count()
    registration_count.short_description = '报名人数'

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'registration_time', 'attended')
    list_filter = ('attended', 'event')
    search_fields = ('user__username', 'event__title')

@admin.register(BookmarkedEvent)
class BookmarkedEventAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'created_at')
    search_fields = ('user__username', 'event__title')