from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from models_registry.models import AIModel
from models_registry.providers import call_model
import json, random

@method_decorator(csrf_exempt, name='dispatch')
class DirectMessageView(View):
    def post(self, request):
        if not request.session.get('is_owner'):
            return JsonResponse({'error':'Unauthorized'},status=403)
        d = json.loads(request.body)
        model_id = d.get('model_id')
        messages = d.get('messages', [])
        model = AIModel.objects.filter(model_id=model_id, is_active=True).first()
        if not model:
            return JsonResponse({'error':'Model not found'},status=404)
        system = (f"You are {model.name} in a private 1-on-1 conversation with the platform owner. "
                  f"Be helpful, honest, and natural. This is a private DM — other models cannot see this.")
        response = call_model(model, messages, system)
        return JsonResponse({'response': response, 'model': model.name})