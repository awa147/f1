"""
URL configuration for campus_activity project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EventCategoryViewSet,
    CampusEventViewSet,
    UserEventRegistrationViewSet,
    UserBookmarkedEventViewSet
)

router = DefaultRouter()
router.register(r'categories', EventCategoryViewSet, basename='category')
router.register(r'events', CampusEventViewSet, basename='event')
router.register(r'my-registrations', UserEventRegistrationViewSet, basename='my-registration')
router.register(r'my-bookmarks', UserBookmarkedEventViewSet, basename='my-bookmark')

urlpatterns = [
    path('', include(router.urls)),
    
    # 自定义动作的独立端点
    path('events/<int:pk>/register/', 
         CampusEventViewSet.as_view({'post': 'register'}), 
         name='event-register'),
    path('events/<int:pk>/bookmark/', 
         CampusEventViewSet.as_view({'post': 'bookmark', 'delete': 'remove_bookmark'}), 
         name='event-bookmark'),
]