from datetime import datetime

from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from . import tests
from .models import Note
from .paginations import NotePagination
from .serializers import NoteSerializer
from .tests import NoteTestCase


class NoteViewSet(ModelViewSet):  # Класс для реализации CRUD операций с заметками

    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = NoteSerializer
    pagination_class = NotePagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['owner']  # Фильтрация по пользователю

    def get_serializer_context(self):  # Добавляем запрос в контекст сериализатора
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def get_queryset(self):  # Получение спсика заметок
        queryset = Note.objects
        queryset = queryset.select_related('owner')  # Объединение с таблицей пользователей
        queryset = queryset.filter(status=True)  # Извлечение только неудаленных записей
        queryset = self.append_date_filters(queryset)  # Добавление фильтра на дату и интервал дат
        queryset = queryset.order_by('-created_at',
                                     '-id')  # Сортировка по дате создания записи и его id в обратном порядке
        return queryset

    def append_date_filters(self, queryset):  # Фильтр по дате и интервалу дат
        date_filters = [
            'created_at',
            'created_at__gte',
            'created_at__lte',
        ]  # Список параметров для фильтрации по дате

        for param_name in date_filters:
            date_param = self.request.query_params.get(param_name)  # Извлечение параметра из запроса
            if date_param:
                is_valid, error_message = self.validate_date(date_param)  # Валидация даты из параметра
                if not is_valid:
                    raise ValidationError({"detail": error_message})

                date_value = datetime.strptime(date_param, '%Y-%m-%d').date()
                queryset = queryset.filter(**{param_name: date_value})  # Добавление фильтра к запросу
        return queryset

    def perform_create(self, serializer):  # Сохранение заметки с присвоением обязательных полей
        return serializer.save(owner=self.request.user, created_at=timezone.now(), status=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()  # Получение заметки, которую необходимо удалить
        is_valid, error_message = self.validate_destroy(request, instance)
        if is_valid:
            return super().destroy(request, *args, **kwargs)
        else:
            raise PermissionDenied({"detail": error_message})

    def perform_destroy(self, instance):  # Выполнение операции удаление заметки
        instance.status = False  # Изменением статуса на неактивный
        instance.save()  # Выполнение операции сохранение заметки

    def validate_destroy(self, request, instance):  # Проверка на возможность обновления заметки
        if instance.owner != request.user:
            return False, "You can only delete your own notes."
        else:
            return True, None

    def update(self, request, *args, **kwargs):  # Обновление заметки
        instance = self.get_object()  # Получение заметки, которую необходимо обновить
        is_valid, error_message = self.validate_update(request, instance)
        if is_valid:
            return super().update(request, *args, **kwargs)  # Данные обновленной заметки
        else:
            raise PermissionDenied({"detail": error_message})

    def validate_update(self, request, instance):  # Проверка на возможность обновления заметки
        time_diff = timezone.now() - instance.created_at
        # Вычисление времени, прошедшего с момента ее создания
        if time_diff.days > 1:  # Невозможно редактировать заметки, созданные более суток назад
            return False, "It has been more than 1 day since the note was created."
        if instance.owner != request.user:  # Невозможно редактировать чужие заметки
            return False, "You can only edit your own notes."
        return True, None  # Разрешаем обновление заметки

    def perform_update(self, serializer):  # Выполнение операции обновление заметки
        note = self.get_object()  # Получение заметки, которую необходимо обновить
        # Объединение изменяемых данных и неизменяемых
        return serializer.save(owner=self.request.user, created_at=note.created_at, status=True)

    def validate_date(self, date_string):  # Валидация даты в формате "YYYY-MM-DD".
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True, None  # Дата валидна
        except ValueError:
            return False, "Invalid date format."
