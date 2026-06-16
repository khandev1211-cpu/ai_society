from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import AIModel
from .providers import fetch_groq_models, fetch_openrouter_models, fetch_gemini_models

def sync_models():
    all_models = (
        fetch_groq_models() +
        fetch_openrouter_models() +
        fetch_gemini_models()
    )
    for m in all_models:
        AIModel.objects.update_or_create(
            model_id=m['model_id'],
            defaults={k:v for k,v in m.items() if k != 'model_id'}
        )
    return len(all_models)

class ModelListView(View):
    def get(self, request):
        models = AIModel.objects.filter(is_active=True, is_free=True)
        data = [{'id':m.id,'model_id':m.model_id,'name':m.name,'provider':m.provider,
                 'color':m.color,'bg_color':m.bg_color,'initials':m.initials} for m in models]
        return JsonResponse({'models': data, 'count': len(data)})

@method_decorator(csrf_exempt, name='dispatch')
class SyncModelsView(View):
    def post(self, request):
        if not request.session.get('is_owner'):
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        count = sync_models()
        return JsonResponse({'synced': count})