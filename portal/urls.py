from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('search/', views.search, name='search'),
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('article/<slug:slug>/comment/', views.add_comment, name='add_comment'),
]
