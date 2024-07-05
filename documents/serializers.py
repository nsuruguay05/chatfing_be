from rest_framework import serializers

from documents.models import Chunk, Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

class ChunkSerializer(serializers.ModelSerializer):
    document = DocumentSerializer(read_only=True)
    class Meta:
        model = Chunk
        fields = '__all__'