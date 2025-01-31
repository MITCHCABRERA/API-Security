from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from .models import Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from .permissions import IsPostAuthor
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.hashers import make_password

# User creation with password hashing (via Django's create_user method)
class UserListCreate(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not password or not email:
            return Response({"error": "Username, email, and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)

        return Response({"message": "User created successfully", "user": {"username": user.username, "email": user.email}}, status=status.HTTP_201_CREATED)


# User creation and assigning to Admin group (role-based access)
class UserCreateAndAssignGroup(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not password or not email:
            return Response({"error": "Username, email, and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Create user with hashed password
        user = User.objects.create_user(username=username, email=email, password=password)

        # Assign user to the Admin group
        admin_group, created = Group.objects.get_or_create(name="Admin")
        user.groups.add(admin_group)

        return Response({
            "message": "User created and assigned to Admin group successfully", 
            "user": {"username": user.username, "email": user.email}
        }, status=status.HTTP_201_CREATED)


# User login with JWT token authentication
class UserLogin(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)


# Post List & Create (Requires token authentication)
class PostListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        author = request.data.get('author')
        if author and not User.objects.filter(id=author).exists():
            return Response({"error": "Author not found."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        
class UserListView(APIView):
    def get(self, request):
        users = User.objects.all()  # Retrieves all users from the database
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

# Secure API view that requires authentication
class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Authenticated!"})


# Post Detail View with role-based permission (Only authors can modify their posts)
class PostDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)  # Check if the user is authorized
        return Response({"content": post.content})


# Comment List & Create
class CommentListCreate(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        post_id = request.data.get('post')
        author_id = request.data.get('author')

        if post_id and not Post.objects.filter(id=post_id).exists():
            return Response({"error": "Post not found."}, status=status.HTTP_400_BAD_REQUEST)

        if author_id and not User.objects.filter(id=author_id).exists():
            return Response({"error": "Author not found."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
