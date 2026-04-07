from rest_framework import serializers
from .models import Complaint, ComplaintAttachment, Category
from accounts.models import CustomUser


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon']


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'full_name', 'role']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class AttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ComplaintAttachment
        fields = ['id', 'filename', 'file_url', 'uploaded_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.file.url) if request else obj.file.url


class ComplaintSerializer(serializers.ModelSerializer):
    complainant = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = Complaint
        fields = ['id', 'complainant', 'type', 'category', 'title', 'description',
                  'location', 'incident_date', 'status', 'status_display',
                  'priority', 'priority_display', 'is_anonymous',
                  'created_at', 'updated_at', 'attachments']
        read_only_fields = ['complainant', 'created_at', 'updated_at']