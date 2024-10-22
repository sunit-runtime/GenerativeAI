from rest_framework import serializers

class PromptSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=True)
    # testcase = serializers.CharField(required=False)