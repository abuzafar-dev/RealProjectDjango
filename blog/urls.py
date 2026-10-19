from django.urls import path

from blog import views

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('posts/new/', views.PostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_update'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
]
