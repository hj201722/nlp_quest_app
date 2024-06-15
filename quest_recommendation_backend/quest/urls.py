# quest/urls.py

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import available_quests, recommend_quest

router = DefaultRouter()
router.register(r"quests", views.QuestViewSet)
router.register(r"feedback", views.FeedbackViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("recommend_quest/", recommend_quest, name="recommend_quest"),
    path("available_quests/", available_quests, name="available_quests"),
]
