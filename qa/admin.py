from django.contrib import admin

from qa.models import Question, Answer, Evaluation

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at', 'updated_at')
    search_fields = ('question',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('short_answer', 'question', 'generative_model', 'method','created_at', 'updated_at')
    list_filter = ('question', 'generative_model', 'method')
    search_fields = ('answer', 'evaluation_author')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    @admin.display(description='Answer')
    def short_answer(self, obj):
        return obj.answer[:150] + '...' if len(obj.answer) > 150 else obj.answer

class AnswerIDFilter(admin.SimpleListFilter):
    title = 'answer ID'
    parameter_name = 'answer_id'

    def lookups(self, request, model_admin):
        return [(obj.answer_id, obj.answer_id) for obj in model_admin.model.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(answer_id=self.value())
        return queryset

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('answer_id', 'like', 'comment', 'author', 'created_at', 'updated_at')
    list_filter = (AnswerIDFilter, 'like', 'author', 'created_at', 'updated_at')
    search_fields = ('comment', 'author')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
