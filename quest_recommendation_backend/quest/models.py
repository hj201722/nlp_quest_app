from django.db import models


class Quest(models.Model):
    quest_id = models.CharField(max_length=10, unique=True)
    quest_name = models.CharField(max_length=100)
    description = models.TextField()
    date_range = models.CharField(max_length=20)
    age_group = models.CharField(max_length=20)
    gender = models.CharField(max_length=20)
    category = models.CharField(max_length=50)
    weight = models.IntegerField(default=0)

    def __str__(self):
        return self.quest_name


class Feedback(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    sentiment_score = models.IntegerField(
        default=0
    )  # -1 for negative, 0 for neutral, 1 for positive
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.quest.quest_name}"
