from django.contrib.auth.models import User
from django.db.models import ForeignKey, Model, DateTimeField, BooleanField, CharField, CASCADE


class Note(Model):
    title = CharField(max_length=120)  # Заголовок записи
    description = CharField(max_length=500)  # Описание записи
    owner = ForeignKey(User, on_delete=CASCADE, blank=True, null=False)  # Создатель записи
    created_at = DateTimeField(blank=True, null=False)  # Дата создания записи
    status = BooleanField(blank=True, null=False)  # Состояние записи: удалена или активна

    def __str__(self):
        return self.title