from rest_framework.serializers import ModelSerializer, CharField, SerializerMethodField

from .models import Note


class NoteSerializer(ModelSerializer):
    # Логин автора
    owner_username = CharField(source='owner.username', read_only=True)

    # Значение для определения, является ли автор запроса автором записи
    is_owner = SerializerMethodField()

    def get_is_owner(self, obj):
        # Проверяем, является ли автор запроса автором записи
        user = self.context.get('user')
        return user == obj.owner

    def to_representation(self, instance):
        # Если пользователь не авторизован, то значение is_owner удаляется
        rep = super().to_representation(instance)
        user = self.context.get('user')
        if not (user and user.is_authenticated):
            rep.pop('is_owner', None)
        return rep

    class Meta:
        model = Note
        fields = ["id", "owner_username", "title", "description", "created_at", "is_owner"]
