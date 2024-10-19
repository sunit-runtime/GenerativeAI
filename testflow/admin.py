from django.contrib import admin
from .models import ResetPasswordRequest, Prompt, TestResult

# Register your models here.


@admin.register(ResetPasswordRequest)
class ResetPasswordRequestAdmin(admin.ModelAdmin):
    list_display = [
        "userEmail",
        "request_at",
        "updated_at",
        "encryptCode",
        "user",
        "verified",
    ]


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ["user", "prompt_text", "created_at"]


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = [
        "prompt",
        "coverage",
        "created_at",
        "code",
        "test_cases",
        "test_output",
        "passed_tests",
        "failed_tests",
    ]
