from rest_framework import serializers
from .models import EventCategory, CampusEvent, EventRegistration, BookmarkedEvent
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = '__all__'

class CampusEventSerializer(serializers.ModelSerializer):
    category = EventCategorySerializer(read_only=True)
    organizer = UserSerializer(read_only=True)
    registration_count = serializers.SerializerMethodField()
    is_registered = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = CampusEvent
        fields = [
            'id', 'title', 'description', 'category', 'location',
            'start_time', 'end_time', 'organizer', 'capacity',
            'cover_image', 'status', 'status_display', 'created_at',
            'is_featured', 'registration_count', 'is_registered',
            'is_bookmarked'
        ]
        read_only_fields = ['organizer', 'created_at', 'registration_count']
    
    def get_registration_count(self, obj):
        return obj.registrations.count()
    
    def get_is_registered(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.registrations.filter(user=request.user).exists()
        return False
    
    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookmarks.filter(user=request.user).exists()
        return False

class EventCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusEvent
        fields = [
            'title', 'description', 'category', 'location',
            'start_time', 'end_time', 'capacity', 'cover_image',
            'status', 'is_featured'
        ]
    
    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise ValidationError("结束时间必须晚于开始时间")
        if data['start_time'] < timezone.now():
            raise ValidationError("不能创建过去时间的活动")
        return data

class EventRegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event = CampusEventSerializer(read_only=True)
    
    class Meta:
        model = EventRegistration
        fields = '__all__'
        read_only_fields = ['user', 'event', 'registration_time', 'attended']

class BookmarkedEventSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event = CampusEventSerializer(read_only=True)
    
    class Meta:
        model = BookmarkedEvent
        fields = '__all__'
        read_only_fields = ['user', 'created_at']