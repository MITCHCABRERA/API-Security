from django.urls import path
from .views import UserListCreate, PostListCreate, CommentListCreate, PostDetailView, UserCreateAndAssignGroup, UserLogin
from . import views
urlpatterns = [
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('users/create-and-assign-group/', UserCreateAndAssignGroup.as_view(), name='user-create-assign-group'),
    path('users/login/', UserLogin.as_view(), name='user-login'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail-view'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:id>/', views.UserDetailView.as_view(), name='user-detail'),
    
]
