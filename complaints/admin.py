from django.contrib import admin
from .models import Complaint, ComplaintAttachment, ComplaintUpdate, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']


class AttachmentInline(admin.TabularInline):
    model = ComplaintAttachment
    extra = 0


class UpdateInline(admin.TabularInline):
    model = ComplaintUpdate
    extra = 0
    readonly_fields = ['updated_by', 'created_at']


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'type', 'complainant', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'type', 'category']
    search_fields = ['title', 'description', 'complainant__username']
    inlines = [AttachmentInline, UpdateInline]
    date_hierarchy = 'created_at'