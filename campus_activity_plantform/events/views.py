from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import EventCategory, CampusEvent, EventRegistration, BookmarkedEvent
from .serializers import (
    EventCategorySerializer,
    CampusEventSerializer,
    EventCreateUpdateSerializer,
    EventRegistrationSerializer,
    BookmarkedEventSerializer
)
from django.utils import timezone
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404

class EventCategoryViewSet(viewsets.ModelViewSet):
    queryset = EventCategory.objects.annotate(event_count=Count('campusevent'))
    serializer_class = EventCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None  # 分类不需要分页

class CampusEventViewSet(viewsets.ModelViewSet):
    queryset = CampusEvent.objects.select_related('category', 'organizer')\
        .prefetch_related('registrations', 'bookmarks')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'status', 'is_featured']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_time', 'created_at']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EventCreateUpdateSerializer
        return CampusEventSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 过滤已过期活动
        show_past = self.request.query_params.get('show_past', 'false').lower() == 'true'
        if not show_past:
            queryset = queryset.filter(end_time__gte=timezone.now())
        
        # 用户特定过滤
        user = self.request.user
        if user.is_authenticated:
            registered = self.request.query_params.get('registered', None)
            if registered == 'true':
                queryset = queryset.filter(registrations__user=user)
            elif registered == 'false':
                queryset = queryset.exclude(registrations__user=user)
            
            bookmarked = self.request.query_params.get('bookmarked', None)
            if bookmarked == 'true':
                queryset = queryset.filter(bookmarks__user=user)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def register(self, request, pk=None):
        event = self.get_object()
        
        if event.registrations.count() >= event.capacity:
            return Response(
                {"detail": "活动人数已满"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if EventRegistration.objects.filter(event=event, user=request.user).exists():
            return Response(
                {"detail": "您已报名该活动"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        registration = EventRegistration.objects.create(
            event=event,
            user=request.user
        )
        
        serializer = EventRegistrationSerializer(registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def bookmark(self, request, pk=None):
        event = self.get_object()
        bookmark, created = BookmarkedEvent.objects.get_or_create(
            event=event,
            user=request.user
        )
        
        if not created:
            return Response(
                {"detail": "已收藏该活动"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = BookmarkedEventSerializer(bookmark)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @bookmark.mapping.delete
    def remove_bookmark(self, request, pk=None):
        event = self.get_object()
        BookmarkedEvent.objects.filter(
            event=event,
            user=request.user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserEventRegistrationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['attended']
    
    def get_queryset(self):
        return EventRegistration.objects.filter(
            user=self.request.user
        ).select_related('event', 'event__category')

class UserBookmarkedEventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BookmarkedEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return BookmarkedEvent.objects.filter(
            user=self.request.user
        ).select_related('event', 'event__category')