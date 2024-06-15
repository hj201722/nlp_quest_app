import logging
import os
import pickle
import re
from datetime import datetime

import numpy as np
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from konlpy.tag import Okt
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.initializers import Orthogonal
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

from .models import Feedback, Quest
from .serializers import FeedbackSerializer, QuestSerializer

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 글로벌 변수
okt = Okt()
stopwords = [
    "의",
    "가",
    "이",
    "은",
    "들",
    "는",
    "좀",
    "잘",
    "걍",
    "과",
    "도",
    "를",
    "으로",
    "자",
    "에",
    "와",
    "한",
    "하다",
]
max_len = 30  # 최대 길이 설정, 필요에 따라 조정
vectorizer = TfidfVectorizer()


def load_resources():
    # 모델 로딩
    try:
        model_path = os.path.join(settings.BASE_DIR, "best_model.h5")
        sentiment_model = load_model(
            model_path, custom_objects={"Orthogonal": Orthogonal}
        )
        logger.info("모델 로딩 성공")
    except Exception as e:
        logger.error(f"모델 로딩 실패: {e}")
        sentiment_model = None

    # 토크나이저 로딩
    try:
        tokenizer_path = os.path.join(settings.BASE_DIR, "tokenizer.pickle")
        with open(tokenizer_path, "rb") as handle:
            tokenizer = pickle.load(handle)
        logger.info("토크나이저 로딩 성공")
    except Exception as e:
        logger.error(f"토크나이저 로딩 실패: {e}")
        tokenizer = None

    return sentiment_model, tokenizer


sentiment_model, tokenizer = load_resources()

date_ranges = {
    "3월~5월 (봄)": range(3, 6),
    "6월~8월 (여름)": range(6, 9),
    "9월~11월 (가을)": range(9, 12),
    "12월~2월 (겨울)": list(range(12, 13)) + list(range(1, 3)),
    "12월 (크리스마스)": [12],
}


@api_view(["POST"])
def recommend_quest(request):
    data = request.data
    current_month = datetime.now().month

    # 날짜 범위 필터
    month_ranges = [dr for dr, months in date_ranges.items() if current_month in months]

    # 필터링 조건 설정
    filter_conditions = Q()

    # 입력 데이터를 모델 필드에 매핑
    if data.get("category"):  # 'category' 입력 처리
        filter_conditions |= Q(category__icontains=data["category"])
    if data.get(
        "description"
    ):  # 'description' 입력 처리, 사용자 인터페이스에서 'indoor_or_outdoor'를 'description'으로 매핑했다고 가정
        filter_conditions |= Q(description__icontains=data["description"])
    if data.get("age_group"):
        filter_conditions |= Q(age_group__icontains=data["age_group"])
    if data.get("gender"):
        filter_conditions |= Q(gender__icontains=data["gender"])

    # 날짜 범위 추가
    filter_conditions &= Q(date_range__in=month_ranges)

    # Quest 모델에서 조건에 맞는 객체 필터링
    quests = Quest.objects.filter(filter_conditions).distinct()

    if quests.exists():
        quest_descriptions = [quest.description for quest in quests]
        quest_vectors = vectorizer.fit_transform(quest_descriptions)

        # 입력 설명 벡터화
        input_description = data.get("input_description", "")
        input_vector = vectorizer.transform([input_description])

        # 코사인 유사도 계산
        similarities = cosine_similarity(input_vector, quest_vectors).flatten()
        quests_with_similarity = list(zip(quests, similarities))
        quests_with_similarity.sort(key=lambda x: (x[1], x[0].weight), reverse=True)

        # 상위 3개 퀘스트 객체 가져오기
        top_quests = quests_with_similarity[:3]
        recommended_quests = [quest for quest, similarity in top_quests]

        result = {
            "message": "퀘스트 추천이 완료되었습니다.",
            "recommended_quests": [
                {
                    "quest_id": quest.quest_id,
                    "quest_name": quest.quest_name,
                    "description": quest.description,
                    "date_range": quest.date_range,
                    "age_group": quest.age_group,
                    "gender": quest.gender,
                    "category": quest.category,
                    "weight": quest.weight,
                }
                for quest in recommended_quests
            ],
        }
    else:
        result = {"message": "유사한 퀘스트를 찾을 수 없습니다."}

    return JsonResponse(result, json_dumps_params={"ensure_ascii": False})


@api_view(["GET"])
def available_quests(request):
    current_month = datetime.now().month
    date_ranges = {
        "3월~5월 (봄)": range(3, 6),
        "6월~8월 (여름)": range(6, 9),
        "9월~11월 (가을)": range(9, 12),
        "12월~2월 (겨울)": list(range(12, 13)) + list(range(1, 3)),
        "12월 (크리스마스)": [12],
    }

    available_quests = Quest.objects.filter(
        date_range__in=[
            key for key, value in date_ranges.items() if current_month in value
        ]
    )

    serializer = QuestSerializer(available_quests, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def feedback_view(request):
    logger.info(f"Received data: {request.data}")
    # 퀘스트 ID와 피드백 텍스트를 로그로 남김
    logger.info(f"Quest ID: {request.data.get('quest')}")
    logger.info(f"Feedback Text: {request.data.get('feedback_text')}")
    serializer = FeedbackSerializer(data=request.data)
    if serializer.is_valid():
        feedback = serializer.save()
        sentiment_score = analyze_sentiment(feedback.feedback_text)
        feedback.sentiment_score = 1 if sentiment_score > 0.5 else -1
        feedback.save()

        quest = feedback.quest
        quest.weight += feedback.sentiment_score
        quest.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        logger.error("Validation Errors: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def preprocess_text(text):
    text = re.sub(r"[^ㄱ-ㅎㅏ-ㅣ가-힣 ]", "", text)
    tokenized = okt.morphs(text, stem=True)
    tokenized = [word for word in tokenized if not word in stopwords]
    encoded = tokenizer.texts_to_sequences([tokenized])
    padded = pad_sequences(encoded, maxlen=max_len)
    return padded


def analyze_sentiment(text):
    preprocessed_text = preprocess_text(text)
    score = float(sentiment_model.predict(preprocessed_text)[0])
    return score


class QuestViewSet(viewsets.ModelViewSet):
    queryset = Quest.objects.all()
    serializer_class = QuestSerializer


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        feedback = serializer.save()

        sentiment_score = analyze_sentiment(feedback.feedback_text)
        feedback.sentiment_score = 1 if sentiment_score > 0.5 else -1
        feedback.save()

        quest = feedback.quest
        quest.weight += feedback.sentiment_score
        quest.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
