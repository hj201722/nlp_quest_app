import csv
import os

from django.core.management.base import BaseCommand
from quest.models import Quest


class Command(BaseCommand):
    help = "Load quests from quest_list.csv"

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        csv_file_path = os.path.join(base_dir, "quest_list.csv")

        self.stdout.write(self.style.SUCCESS(f"Loading quests from {csv_file_path}"))

        try:
            with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    quest, created = Quest.objects.update_or_create(
                        quest_id=row["퀘스트 ID"],
                        defaults={
                            "quest_name": row["퀘스트 이름"],
                            "description": row["설명"],
                            "date_range": row["날짜"],
                            "age_group": row["나이대"],
                            "gender": row["성별"],
                            "category": row["카테고리"],
                            "weight": 0,
                        },
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f'Quest "{quest.quest_name}" created')
                        )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(f'Quest "{quest.quest_name}" updated')
                        )
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {csv_file_path}"))
        except KeyError as e:
            self.stdout.write(self.style.ERROR(f"Key error: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
