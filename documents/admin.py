from django.contrib import admin

from documents.models import Document, Chunk

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'active', 'created_at', 'updated_at')
    list_filter = ('active', 'created_at', 'updated_at')
    search_fields = ('title', 'url')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = ('document', 'chunk', 'position', 'created_at', 'updated_at')
    list_filter = ('document', 'position', 'created_at', 'updated_at')
    search_fields = ('document', 'chunk')
    ordering = ('document', 'position')
    readonly_fields = ('created_at', 'updated_at')