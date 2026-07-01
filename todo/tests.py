from django.test import TestCase, Client
from django.utils import timezone
from datetime import datetime
from .models import Task

class TaskModelTestCase(TestCase):
    # --- 作成に関するテスト ---
    def test_create_task_with_due_date(self):
        """締め切り付きタスクが正しく作成・保存されるか"""
        due = timezone.make_aware(datetime(2023, 6, 30, 23, 59, 59))
        task = Task.objects.create(title='task1', due_at=due)
        
        # データベースから再取得して検証
        saved_task = Task.objects.get(pk=task.pk)
        self.assertEqual(saved_task.title, 'task1')
        self.assertFalse(saved_task.completed)
        self.assertEqual(saved_task.due_at, due)

    def test_create_task_without_due_date(self):
        """締め切りなしタスクが正しく作成・保存されるか"""
        task = Task.objects.create(title='task2')
        
        saved_task = Task.objects.get(pk=task.pk)
        self.assertEqual(saved_task.title, 'task2')
        self.assertFalse(saved_task.completed)
        self.assertIsNone(saved_task.due_at)

    # --- is_overdue メソッドのテスト ---
    def test_is_overdue_past(self):
        """締め切りを過ぎている場合、Trueを返す"""
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
        current = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 0))
        task = Task.objects.create(title='past_task', due_at=due)
        self.assertTrue(task.is_overdue(current))

    def test_is_overdue_none(self):
        """締め切りのないタスクはFalseを返す"""
        current = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 0))
        task = Task.objects.create(title='no_due_task', due_at=None)
        self.assertFalse(task.is_overdue(current))

    def test_is_overdue_equal(self):
        """締め切りと現在時刻が同じ場合、Falseを返す"""
        due = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 0))
        current = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 0))
        task = Task.objects.create(title='equal_task', due_at=due)
        self.assertFalse(task.is_overdue(current))

    def test_is_overdue_future(self):
        """締め切りが未来の場合、Falseを返す"""
        due = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 1))
        current = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 0))
        task = Task.objects.create(title='future_task', due_at=due)
        self.assertFalse(task.is_overdue(current))



class TodoViewTestCase(TestCase):
    def test_index_get(self):
        client = Client()
        data = {'title': 'TestTask', 'due_at': '2024-06-30 23:59:59'}
        response = client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(len(response.context['tasks']), 0)

    def test_index_get_order_post(self):
        task1 = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task1.save()
        task2 = Task(title='task2', due_at=timezone.make_aware(datetime(2024, 8, 1)))
        task2.save()
        client = Client()
        response = client.get('/?order=post')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(response.context['tasks'][0], task2)
        self.assertEqual(response.context['tasks'][1], task1)

    def test_index_get_order_due(self):
        task1 = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 8, 1)))
        task1.save()
        task2 = Task(title='task2', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task2.save()
        client = Client()
        response = client.get('/?order=due')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['tasks'][0], task2) # 締め切りが早いtask2が先
        self.assertEqual(response.context['tasks'][1], task1)
    
    def test_index_post(self):
        client = Client()
        data = {'title': 'TestTask', 'due_at': '2024-06-30 23:59:59'}
        response = client.post('/', data)

        self.assertEqual(response.status_code, 200)
        # データベースに1件登録されているか確認
        self.assertEqual(Task.objects.count(), 1)
        saved_task = Task.objects.first()
        self.assertEqual(saved_task.title, 'TestTask')

    def test_detail_get_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.get('/{}/'.format(task.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/detail.html')
        self.assertEqual(response.context['task'], task)

    def test_detail_get_fail(self):
        client = Client()
        response = client.get('/1/')

        self.assertEqual(response.status_code, 404)