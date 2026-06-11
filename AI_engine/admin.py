from django.contrib import admin
from .models import LLMUsageLog, AIPromptResponseLog


# =========================
# LLM USAGE LOG ADMIN
# =========================
@admin.register(LLMUsageLog)
class LLMUsageLogAdmin(admin.ModelAdmin):

    list_display = (
        "model",
        "user",
        "input_tokens",
        "output_tokens",
        "cost_usd",
        "success",
        "created_at",
    )

    list_filter = (
        "model",
        "success",
    )

    search_fields = (
        "model",
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "id",
        "created_at",
    )

    ordering = ("-created_at",)


# =========================
# AI PROMPT RESPONSE LOG ADMIN
# =========================
@admin.register(AIPromptResponseLog)
class AIPromptResponseLogAdmin(admin.ModelAdmin):

    list_display = (
        "model",
        "user",
        "prompt_tokens",
        "response_tokens",
        "latency_ms",
        "is_successful",
        "created_at",
    )

    list_filter = (
        "model",
        "is_successful",
    )

    search_fields = (
        "model",
        "user__username",
        "user__email",
        "prompt_text",
    )

    readonly_fields = (
        "id",
        "created_at",
    )

    ordering = ("-created_at",)