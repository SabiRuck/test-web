from django.contrib import admin
from .models import User, Question, Answer, Test, TestQuestion, Result, StudentResponse

# zobrazeni odpovede priamo v detaile otázky
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 3  # Predvolene zobrazí 3 polia pre odpovede

# otazky k testu cez prepojovací model
class TestQuestionInline(admin.TabularInline):
    model = TestQuestion
    extra = 1

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'type', 'points')
    list_filter = ('type',)
    inlines = [AnswerInline]  # Umožní vytvárať odpovede priamo pri otázke

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'time_limit', 'is_published')
    list_filter = ('subject', 'is_published')
    inlines = [TestQuestionInline]  # pridavas otazky 

admin.site.register(User)
admin.site.register(Result)
admin.site.register(Answer)
admin.site.register(TestQuestion)
admin.site.register(StudentResponse)