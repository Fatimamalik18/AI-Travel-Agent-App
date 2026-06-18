from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from .models import LLMUsageLog, AIPromptResponseLog
from .serializers import LLMUsageLogSerializer, AIPromptResponseLogSerializer


# =========================
# LLM USAGE LOG
# =========================

class LLMUsageLogListView(generics.ListAPIView):
    """
    GET /api/ai/llm-logs/
    - Normal user → sirf apne logs
    - Admin → sab users ke logs (?all=true)
    """
    serializer_class   = LLMUsageLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields   = ['model', 'success', 'trip_id']
    search_fields      = ['model']

    def get_queryset(self):
        user = self.request.user
        # Admin sab dekh sakta hai
        if user.is_staff and self.request.query_params.get('all') == 'true':
            return LLMUsageLog.objects.all().select_related('user')
        return LLMUsageLog.objects.filter(user=user)


class LLMUsageLogDestroyView(generics.DestroyAPIView):
    """
    DELETE /api/ai/llm-logs/<id>/   → Admin only
    """
    serializer_class   = LLMUsageLogSerializer
    permission_classes = [IsAdminUser]
    queryset           = LLMUsageLog.objects.all()


# =========================
# AI PROMPT RESPONSE LOG
# =========================

class AIPromptLogListView(generics.ListAPIView):
    """
    GET /api/ai/prompt-logs/
    - Normal user → sirf apne logs
    - Admin → sab users ke logs (?all=true)
    """
    serializer_class   = AIPromptResponseLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields   = ['model', 'is_successful', 'trip_id']
    search_fields      = ['model']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff and self.request.query_params.get('all') == 'true':
            return AIPromptResponseLog.objects.all().select_related('user')
        return AIPromptResponseLog.objects.filter(user=user)


class AIPromptLogDestroyView(generics.DestroyAPIView):
    """
    DELETE /api/ai/prompt-logs/<id>/   → Admin only
    """
    serializer_class   = AIPromptResponseLogSerializer
    permission_classes = [IsAdminUser]
    queryset           = AIPromptResponseLog.objects.all()