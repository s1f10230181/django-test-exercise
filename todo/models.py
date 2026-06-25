# todo/models.py
from django.db import models
from django.utils import timezone

class Task(models.Model):
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    posted_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField(null=True, blank=True)

    def is_overdue(self, dt):
        if self.due_at is None:
            return False
        return self.due_at < dt

class TaskModelTestCase(TestCase):
    # ... (既存の test_is_overdue_future は省略)

    def test_is_overdue_past(self):
        """2024/6/30 23:59:59締め切りのタスクは、2024/7/1 0時に対してTrueを返す"""
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
        current = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 0))
        task = Task(title='task2', due_at=due)
        task.save()

        self.assertTrue(task.is_overdue(current))

    def test_is_overdue_none(self):
        """締め切りのないタスクは、2024/7/1 0時に対してFalseを返す"""
        due = None
        current = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 0))
        task = Task(title='task3', due_at=due)
        task.save()

        self.assertFalse(task.is_overdue(current))
