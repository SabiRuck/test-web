from django.urls import path
from quiz import views
from django.contrib.auth import views as auth_views
from django.contrib import admin

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='quiz/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Testy
    path('dashboard/novy-test/', views.vytvor_test, name='vytvor_test'),
    path('test/<int:test_id>/', views.detail_testu, name='detail_testu'),
    path('test/<int:test_id>/nova-otazka/', views.vytvor_otazku, name='vytvor_otazku'),
    path('test/<int:test_id>/zmaz-otazku/<int:tq_id>/', views.zmaz_otazku_z_testu, name='zmaz_otazku_z_testu'),
    path('test/<int:test_id>/banka/', views.banka_otazok, name='banka_otazok'),
    path('test/<int:test_id>/banka/pridaj/<int:question_id>/', views.pridaj_otazku_z_banky, name='pridaj_otazku_z_banky'),
    # Správa tried – len admin
    path('admin-panel/triedy/', views.sprava_tried, name='sprava_tried'),
    path('admin-panel/triedy/<int:trieda_id>/zmaz/', views.zmaz_triedu, name='zmaz_triedu'),
    path('admin-panel/ziak/<int:profil_id>/zarad/', views.zarad_ziaka, name='zarad_ziaka'),
    path('admin/', admin.site.urls),
    path('test/<int:test_id>/prepni-stav/', views.prepni_stav_testu, name='prepni_stav_testu'),
    path('test/<int:test_id>/spustit/', views.spustit_test, name='spustit_test'),
    path('vysledok/<int:result_id>/', views.detail_vysledku, name='detail_vysledku'),
    path('test/<int:test_id>/vysledky/', views.vysledky_testu, name='vysledky_testu'),
    path('test/<int:test_id>/uprav/', views.uprav_test, name='uprav_test'),

]