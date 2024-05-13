import os
from django import setup
from datetime import timedelta
from django.test import TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
setup()

from .models import Note
from .serializers import NoteSerializer
from django.contrib.auth.models import User


class NoteTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        cur_time = timezone.now()
        self.user_1 = User.objects.create(username='user1', password="qwerty")
        self.user_2 = User.objects.create(username='user2', password="qwerty")
        self.user_3 = User.objects.create(username='user3', password="qwerty")
        self.note_1 = Note.objects.create(id=1, title="VK",
                                          description="Известная как VK Group до 12 октября 2021 года, является российской технологической компанией",
                                          owner=self.user_1, created_at=cur_time,
                                          status=True)
        self.note_2 = Note.objects.create(id=2, title="ВКонтакте",
                                          description="Самая популярная соцсеть и первое суперприложение в Роcсии",
                                          owner=self.user_2, created_at=cur_time - timedelta(days=5),
                                          status=True)
        self.note_3 = Note.objects.create(id=3, title="Одноклассники",
                                          description="Первая соцсеть в России, развлекательная платформа с играми, видео и музыкой",
                                          owner=self.user_2, created_at=cur_time,
                                          status=False)
        self.note_4 = Note.objects.create(id=4, title="VK Музыка",
                                          description="Огромная библиотека треков и плейлистов, умные рекомендации, аудиокниги, подкасты и радио",
                                          owner=self.user_1, created_at=cur_time - timedelta(days=6),
                                          status=False)
        self.note_5 = Note.objects.create(id=5, title="VK Клипы",
                                          description="Бесконечная лента коротких вертикальных роликов с шоу, трендами и челленджами",
                                          owner=self.user_3, created_at=cur_time - timedelta(hours=3),
                                          status=True)
        self.note_6 = Note.objects.create(id=6, title="VK Видео",
                                          description="Видеоплатформа с кино, трансляциями, эксклюзивными проектами и миллионами роликов",
                                          owner=self.user_1, created_at=cur_time - timedelta(days=1),
                                          status=True)
        self.note_7 = Note.objects.create(id=7, title="VK Знакомства",
                                          description="Дейтинг-сервис: алгоритмы предлагают анкеты людей с совпадающими интересами",
                                          owner=self.user_2, created_at=cur_time,
                                          status=True)
        self.note_8 = Note.objects.create(id=8, title="Дзен",
                                          description="Платформа для создания и просмотра контента, где умные алгоритмы помогают всем найти свою аудиторию",
                                          owner=self.user_2, created_at=cur_time - timedelta(days=10),
                                          status=False)
        self.note_9 = Note.objects.create(id=9, title="VK Фитнес",
                                          description="Платформа объединяет популярные спортивные сервисы VK Шаги, VK Тренировки и VK Бег",
                                          owner=self.user_2, created_at=cur_time,
                                          status=False)

    def test_serializer_with_auth(self):
        # Тест првоерки сериализатора с авторизацией
        note = self.note_1
        data = {
            "id": note.id,
            "owner_username": note.owner.username,
            "title": note.title,
            "description": note.description,
            "created_at": note.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "is_owner": True
        }
        serializer = NoteSerializer(note)
        serializer.context['user'] = self.user_1
        serializer_data = serializer.data
        self.assertEqual(data, serializer_data)

    def test_serializer_without_auth(self):
        # Тест првоерки сериализатора без авторизацией
        note = self.note_1
        data = {
            "id": note.id,
            "owner_username": note.owner.username,
            "title": note.title,
            "description": note.description,
            "created_at": note.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }
        serializer = NoteSerializer(note)
        serializer_data = serializer.data
        self.assertEqual(data, serializer_data)

    def test_get_all_notes(self):
        # Тест получения своих заметок
        # 7,1,5,6,2
        url = reverse('note-list')
        response = self.client.get(url)
        serializer_data = NoteSerializer(
            [self.note_7, self.note_1, self.note_5, self.note_6, self.note_2], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer_data)

    def test_get_active_note(self):
        # Тест поулчение одной заметки
        note_id = 1
        user = self.user_1
        url = reverse('note-detail', kwargs={'pk': note_id})
        response = self.client.get(url)
        serializer = NoteSerializer(self.note_1)
        serializer_data = serializer.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)

    def test_get_deleted_note(self):
        # Тест получения удаленной заметки
        note_id = 4
        self.client.force_login(self.user_1)
        url = reverse('note-detail', kwargs={'pk': note_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_someone_note(self):
        # Тест получения чужой заметки
        note_id = 3
        self.client.force_login(self.user_1)
        url = reverse('note-detail', kwargs={'pk': note_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_nonexistent_note(self):
        # Тест получения не существующей заметки
        note_id = 100
        self.client.force_login(self.user_1)
        url = reverse('note-detail', kwargs={'pk': note_id})
        delete_response = self.client.get(url)
        self.assertEqual(delete_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_note(self):
        # Тест удаления своей заметки
        note_id = 1
        self.client.force_login(self.user_1)
        url = reverse('note-detail', kwargs={'pk': note_id})
        delete_response = self.client.delete(url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        note = Note.objects.get(id=note_id)
        self.assertFalse(note.status)

    def test_delete_someone_note(self):
        # Тест удаления чужой заметки
        note_id = 5
        self.client.force_login(self.user_1)
        url = reverse('note-detail', kwargs={'pk': note_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_nonexistent_note(self):
        # Тест удаления не существующей заметки
        note_id = 100
        self.client.force_login(self.user_1)
        url = reverse('note-detail', kwargs={'pk': note_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_note(self):
        # Тест публикации новой заметки
        data = {
            "title": "Ответы",
            "description": "Сервис для поиска ответа на любой вопрос и обмена опытом",
        }
        self.client.force_login(self.user_1)
        url = reverse('note-list')
        count = Note.objects.count()
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), count + 1)  # Проверяем увеличение количества заметок
        note = Note.objects.last()
        self.assertTrue(
            data['title'] == note.title and
            data['description'] == note.description)  # Сравниваем изначальные даныне с сохраненными

    def test_put_note(self):
        # Тест изменения не существующей заметки
        note_id = 1
        old_note = Note.objects.get(id=note_id)
        data = {
            "owner": 2,
            "created_at": timezone.now(),
            "title": "Ответы",
            "description": "Сервис для поиска ответа на любой вопрос и обмена опытом",
        }
        self.client.force_login(self.user_1)
        url = reverse('note-detail', kwargs={'pk': note_id})
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_note = Note.objects.get(id=note_id)
        self.assertTrue(
            old_note.owner == new_note.owner
            and old_note.created_at == new_note.created_at and new_note.status)  # Приверка низменяемых полей
        self.assertTrue(
            data["title"] == new_note.title
            and data["description"] == new_note.description and new_note.status)  # Приверка изменяемых полей

    def test_put_someone_note(self):
        # Тест изменения чужой заметки
        note_id = 5
        data = {
            "title": "Ответы",
            "description": "Сервис для поиска ответа на любой вопрос и обмена опытом",
        }
        self.client.force_login(self.user_1)
        url = reverse('note-detail', kwargs={'pk': note_id})
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_nonexistent_note(self):
        # Тест изменения не существующей заметки
        note_id = 100
        data = {
            "title": "Ответы",
            "description": "Сервис для поиска ответа на любой вопрос и обмена опытом",
        }
        self.client.force_login(self.user_1)
        url = reverse('note-detail', kwargs={'pk': note_id})
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
