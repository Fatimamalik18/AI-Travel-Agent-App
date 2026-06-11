import uuid
from django.db import models
from accounts.models import CustomUser


# =========================
# LLM USAGE LOG
# =========================
class LLMUsageLog(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="llm_usage_logs"
    )

    trip_id = models.UUIDField(
        null=True,
        blank=True
    )

    model = models.CharField(max_length=100)

    input_tokens = models.IntegerField()

    output_tokens = models.IntegerField()

    cost_usd = models.DecimalField(
        max_digits=10,
        decimal_places=6
    )

    success = models.BooleanField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "llm_usage_logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.model} - {self.user}"


# =========================
# AI PROMPT RESPONSE LOG
# =========================
class AIPromptResponseLog(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="ai_prompt_logs"
    )

    trip_id = models.UUIDField(
        null=True,
        blank=True
    )

    prompt_text = models.TextField()

    response_text = models.TextField()

    model = models.CharField(
        max_length=100
    )

    prompt_tokens = models.IntegerField()

    response_tokens = models.IntegerField()

    latency_ms = models.IntegerField(
        null=True,
        blank=True
    )

    is_successful = models.BooleanField(
        default=True
    )

    error_message = models.TextField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "ai_prompt_response_logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.model} - {self.user}"