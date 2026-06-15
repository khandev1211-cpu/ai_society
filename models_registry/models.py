from django.db import models

class AIModel(models.Model):
    PROVIDER_CHOICES = [('groq','Groq'),('openrouter','OpenRouter'),('gemini','Gemini')]
    model_id   = models.CharField(max_length=200, unique=True)
    name       = models.CharField(max_length=200)
    provider   = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    is_free    = models.BooleanField(default=True)
    is_active  = models.BooleanField(default=True)
    color      = models.CharField(max_length=20, default='#a78bfa')
    bg_color   = models.CharField(max_length=50, default='rgba(108,71,255,0.2)')
    initials   = models.CharField(max_length=4, default='AI')
    last_synced = models.DateTimeField(auto_now=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['provider', 'name']

    def __str__(self):
        return f"{self.name} ({self.provider})"
