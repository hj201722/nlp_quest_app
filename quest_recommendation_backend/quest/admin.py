# quests/admin.py

from django.contrib import admin

from .models import Feedback, Quest


@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = (
        "quest_id",
        "quest_name",
        "date_range",
        "age_group",
        "gender",
        "category",
        "weight",
    )
    search_fields = ("quest_name", "description", "date_range", "category")
    list_filter = ("date_range", "age_group", "gender", "category")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("quest", "feedback_text", "sentiment_score", "created_at")
    search_fields = ("quest__quest_name", "feedback_text")
    list_filter = ("sentiment_score", "created_at")
    list_select_related = ("quest",)
