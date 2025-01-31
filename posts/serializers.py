from rest_framework import serializers
from .models import User, Post, Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # You can add more fields here if needed

class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for the Post model.
    Includes a nested relationship for comments, which are displayed as string representations.
    """
    comments = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'created_at', 'comments']


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comment model.
    Ensures that both the related post and author are valid.
    """
    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'post', 'created_at']

    def validate_post(self, value):
        """
        Validates if the provided post exists.
        """
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Post not found.")
        return value

    def validate_author(self, value):
        """
        Validates if the provided author exists.
        """
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Author not found.")
        return value
