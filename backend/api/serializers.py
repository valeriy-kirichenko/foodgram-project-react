from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import Subscribe, User


class CustomUserSerializer(UserSerializer):
    is_subscribe = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribe'
        )
        read_only_fields = ('is_subscribe',)

    def get_is_subscribe(self, obj):
        return Subscribe.objects.filter(
            user__username=self.context['request'].user,
            author__username=obj
        ).exists()
