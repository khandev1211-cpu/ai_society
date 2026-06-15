from django.db import models
import uuid

class Room(models.Model):
    TYPE_CHOICES = [('group','Group'),('dm','Direct')]
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name       = models.CharField(max_length=100)
    slug       = models.SlugField(max_length=100, unique=True)
    type       = models.CharField(max_length=10, choices=TYPE_CHOICES, default='group')
    dm_model_id = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.name

class Message(models.Model):
    SENDER_CHOICES = [('user','User'),('ai','AI')]
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room        = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=5, choices=SENDER_CHOICES)
    sender_name = models.CharField(max_length=200)
    model_id    = models.CharField(max_length=200, blank=True)
    provider    = models.CharField(max_length=20, blank=True)
    color       = models.CharField(max_length=20, default='#a78bfa')
    bg_color    = models.CharField(max_length=50, default='rgba(108,71,255,0.2)')
    initials    = models.CharField(max_length=4, default='AI')
    content     = models.TextField()
    tags        = models.JSONField(default=list)
    is_autonomous = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta: ordering = ['created_at']

    def to_dict(self):
        return {
            'id': str(self.id),
            'room': str(self.room_id),
            'sender_type': self.sender_type,
            'sender_name': self.sender_name,
            'model_id': self.model_id,
            'provider': self.provider,
            'color': self.color,
            'bg_color': self.bg_color,
            'initials': self.initials,
            'content': self.content,
            'tags': self.tags,
            'is_autonomous': self.is_autonomous,
            'created_at': self.created_at.strftime('%I:%M %p'),
        }
