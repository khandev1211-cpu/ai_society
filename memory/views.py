from django.http import JsonResponse
from django.views import View
from .models import SharedMemory, PrivateMemory
import json

class SharedMemoryView(View):
    def get(self, request):
        if not request.session.get('is_owner'):
            return JsonResponse({'error':'Unauthorized'},status=403)
        mems = SharedMemory.objects.all()[:50]
        return JsonResponse({'memories':[{'content':m.content,'model':m.source_model,'time':m.created_at.strftime('%b %d %H:%M')} for m in mems]})

    def post(self, request):
        if not request.session.get('is_owner'):
            return JsonResponse({'error':'Unauthorized'},status=403)
        d = json.loads(request.body)
        SharedMemory.objects.create(content=d['content'],source_model=d.get('model',''),room_slug=d.get('room','general'))
        return JsonResponse({'ok':True})

class PrivateMemoryView(View):
    def get(self, request, model_id):
        if not request.session.get('is_owner'):
            return JsonResponse({'error':'Unauthorized'},status=403)
        mems = PrivateMemory.objects.filter(model_id=model_id)[:50]
        return JsonResponse({'memories':[{'content':m.content,'time':m.created_at.strftime('%b %d %H:%M')} for m in mems]})
