from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from .models import Room, Message

class LoginView(View):
    def get(self, request):
        if request.session.get('is_owner'):
            return redirect('app')
        return render(request, 'index.html')

    def post(self, request):
        data = __import__('json').loads(request.body)
        u = data.get('username','').strip()
        p = data.get('password','')
        if u == settings.OWNER_USERNAME and p == settings.OWNER_PASSWORD:
            request.session['is_owner'] = True
            request.session.set_expiry(86400 * 30)
            return JsonResponse({'ok': True})
        return JsonResponse({'error': 'Invalid credentials'}, status=401)

class LogoutView(View):
    def post(self, request):
        request.session.flush()
        return JsonResponse({'ok': True})

class AppView(View):
    def get(self, request):
        return render(request, 'index.html')

class SessionView(View):
    def get(self, request):
        return JsonResponse({'is_owner': bool(request.session.get('is_owner'))})

class RoomHistoryView(View):
    def get(self, request, slug):
        room = Room.objects.filter(slug=slug).first()
        if not room:
            return JsonResponse({'messages': []})
        msgs = Message.objects.filter(room=room).order_by('-created_at')[:100]
        return JsonResponse({'messages': [m.to_dict() for m in reversed(msgs)]})
