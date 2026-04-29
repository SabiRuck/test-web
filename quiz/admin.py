from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User as DjangoUser
from .models import Profil, Question, Answer, Test, TestQuestion, Result, StudentResponse

# 1. ROZŠÍRENIE ADMINA PRE POUŽÍVATEĽA
class ProfilInline(admin.StackedInline):
    model = Profil
    can_delete = False
    verbose_name_plural = 'Doplnkové údaje (vek, rola...)'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfilInline,)

# Odhlásime pôvodný User a prihlásime ten náš s Profilom
try:
    admin.site.unregister(DjangoUser)
except admin.sites.NotRegistered:
    pass
admin.site.register(DjangoUser, UserAdmin)

# 2. TVOJA LOGIKA PRE OTÁZKY A TESTY (toto máš super)
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 3 

class TestQuestionInline(admin.TabularInline):
    model = TestQuestion
    extra = 1

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'type', 'points')
    list_filter = ('type',)
    inlines = [AnswerInline]

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'time_limit', 'is_published')
    list_filter = ('subject', 'is_published')
    inlines = [TestQuestionInline]

# 3. ZVYŠNÉ REGISTRÁCIE
admin.site.register(Result)
admin.site.register(StudentResponse)
# admin.site.register(Answer) # Môžeš nechať zakomentované, ak ich upravuješ v QuestionAdmin
# admin.site.register(TestQuestion) # Môžeš nechať zakomentované, ak ich upravuješ v TestAdmin