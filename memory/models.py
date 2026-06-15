from django.db import models
import uuid

class SharedMemory(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content    = models.TextField()
    source_model = models.CharField(max_length=200)
    room_slug  = models.CharField(max_length=100, default='general')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: ordering = ['-created_at']

class PrivateMemory(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_id   = models.CharField(max_length=200)
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: ordering = ['-created_at']
