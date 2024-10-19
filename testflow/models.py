from django.db import models
from django.contrib.auth.models import User

class Prompt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.prompt_text[:30]}"

class TestResult(models.Model):
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    test_output = models.TextField()
    coverage = models.FloatField()
    passed_tests = models.IntegerField()
    failed_tests = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.TextField()
    test_cases = models.TextField()

    def __str__(self):
        return f"Test Results for {self.prompt}"

class ResetPasswordRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    encryptCode = models.TextField()
    request_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    userEmail = models.EmailField()
    verified = models.BooleanField(default=False)