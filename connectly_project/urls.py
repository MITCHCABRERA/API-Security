from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),  # For the browsable API
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Token obtain
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Token refresh
    path('api/', include('posts.urls')), 
]
