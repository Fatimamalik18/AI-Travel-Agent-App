from rest_framework import serializers
from .models import LLMUsageLog, AIPromptResponseLog


class LLMUsageLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = LLMUsageLog
        fields = [
            'id', 'username', 'trip_id', 'model',
            'input_tokens', 'output_tokens', 'cost_usd',
            'success', 'created_at'
        ]
        read_only_fields = fields


class AIPromptResponseLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AIPromptResponseLog
        fields = [
            'id', 'username', 'trip_id', 'model',
            'prompt_text', 'response_text',
            'prompt_tokens', 'response_tokens',
            'latency_ms', 'is_successful', 'error_message',
            'created_at'
        ]
        read_only_fields = fields