import csv
import os
import sqlite3
from datetime import datetime

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

        current_month = datetime.now().month

        # 달 범위를 월의 숫자로 매핑
        date_ranges = {
            "3월~5월 (봄)": range(3, 6),
            "6월~8월 (여름)": range(6, 9),
            "9월~11월 (가을)": range(9, 12),
            "12월~2월 (겨울)": list(range(12, 13)) + list(range(1, 3)),
            "12월 (크리스마스)": [12],
        }

        try:
            with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    quest_date_range = row["날짜"]
                    if current_month in date_ranges.get(quest_date_range, []):
                        quest, created = Quest.objects.get_or_create(
                            quest_id=row["퀘스트 ID"],
                            quest_name=row["퀘스트 이름"],
                            description=row["설명"],
                            date_range=row["날짜"],
                            age_group=row["나이대"],
                            gender=row["성별"],
                            category=row["카테고리"],
                            weight=0,
                        )
                        if created:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Quest "{quest.quest_name}" created'
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Quest "{quest.quest_name}" updated'
                                )
                            )
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {csv_file_path}"))
        except KeyError as e:
            self.stdout.write(self.style.ERROR(f"Key error: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
