from rest_framework import serializers
from .models import AnalyticsResult, AnalyticsTask, DataUpdateLog, AnalyticsCache

class AnalyticsResultSerializer(serializers.ModelSerializer):
    analysis_type_display = serializers.CharField(source='get_analysis_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_at_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalyticsResult
        fields = [
            'id', 'analysis_type', 'analysis_type_display', 'status', 'status_display',
            'results', 'error_message', 'created_at', 'created_at_formatted', 'updated_at',
            'processed_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_created_at_formatted(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')

class AnalyticsTaskSerializer(serializers.ModelSerializer):
    analysis_type_display = serializers.CharField(source='get_analysis_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalyticsTask
        fields = [
            'id', 'task_id', 'analysis_type', 'analysis_type_display', 'status', 'status_display',
            'created_at', 'started_at', 'completed_at', 'duration', 'result', 'error_message'
        ]
        read_only_fields = ['id', 'created_at', 'started_at', 'completed_at']
    
    def get_duration(self, obj):
        if obj.started_at and obj.completed_at:
            duration = obj.completed_at - obj.started_at
            return str(duration.total_seconds()) + 's'
        return None

class DataUpdateLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataUpdateLog
        fields = ['id', 'model_name', 'record_id', 'action', 'triggered_analytics', 'created_at']
        read_only_fields = ['id', 'created_at']

class AnalyticsCacheSerializer(serializers.ModelSerializer):
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AnalyticsCache
        fields = ['id', 'cache_key', 'data', 'expires_at', 'created_at', 'is_expired']
        read_only_fields = ['id', 'created_at']

class AnalyticsRequestSerializer(serializers.Serializer):
    """Serializer for analytics request parameters"""
    analysis_type = serializers.ChoiceField(choices=AnalyticsResult.ANALYSIS_TYPES)
    force_refresh = serializers.BooleanField(default=False)
    cache_duration = serializers.IntegerField(default=3600, min_value=60, max_value=86400)

class AnalyticsResponseSerializer(serializers.Serializer):
    """Serializer for analytics response data"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.JSONField(required=False)
    task_id = serializers.CharField(required=False)
    cached = serializers.BooleanField(default=False)
