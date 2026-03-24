from django.urls import path
from . import views
from .views import register_view

urlpatterns = [
    path('', views.story_list, name='story_list'),
    path('story/<int:story_id>/', views.story_detail, name='story_detail'),
    path('chapter/<int:chapter_id>/', views.chapter_detail, name='chapter_detail'),
    path('search/', views.search_stories, name='search_stories'),
    path('search-ajax/', views.search_ajax, name='search_ajax'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('comment/<int:story_id>/', views.add_comment, name='add_comment'),
    path('rate/<int:story_id>/', views.rate_story, name='rate_story'),
    path('tts/', views.tts_fpt, name='tts_fpt'),
    path('follow/<int:story_id>/', views.follow_story, name='follow_story'),
    path('theo-doi/', views.followed_stories, name='followed_stories'),
    path('lich-su/', views.reading_history, name='reading_history'),
    path('register/', register_view, name='register'),
    path('the-loai/<slug:slug>/', views.category_view, name='category'),
]
