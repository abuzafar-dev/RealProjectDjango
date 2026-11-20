from django.urls import path

from blog import views

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('authors/<str:username>/', views.author_detail, name='author_detail'),
    path('posts/new/', views.PostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_update'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('comments/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
]
