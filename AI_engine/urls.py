from django.urls import path
from . import views

app_name = 'ai_engine'

urlpatterns = [
    # LLM Usage Logs
    path('ai/llm-logs/',views.LLMUsageLogListView.as_view(),name='llm-log-list'),
    path('ai/llm-logs/<uuid:pk>/',views.LLMUsageLogDestroyView.as_view(),name='llm-log-delete'),

    # AI Prompt Response Logs
    path('ai/prompt-logs/',views.AIPromptLogListView.as_view(),name='prompt-log-list'),
    path('ai/prompt-logs/<uuid:pk>/',views.AIPromptLogDestroyView.as_view(),name='prompt-log-delete'),
]
