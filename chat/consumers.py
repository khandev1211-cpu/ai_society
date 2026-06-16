import json, re, random, asyncio, logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_slug = self.scope['url_route']['kwargs']['room_slug']
        self.room_group = f'chat_{self.room_slug}'
        self.is_owner = self.scope['session'].get('is_owner', False)
        self._active = True
        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()
        history = await self.get_history()
        await self.send(json.dumps({'type': 'history', 'messages': history}))
        models = await self.get_models()
        await self.send(json.dumps({'type': 'model_list', 'models': models}))

    async def disconnect(self, code):
        self._active = False
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        if not self.is_owner:
            return
        try:
            data = json.loads(text_data)
        except Exception:
            return
        msg_type = data.get('type', 'message')
        if msg_type == 'message':
            content = data.get('content', '').strip()
            if not content:
                return
            user_msg = await self.save_message(
                sender_type='user', sender_name='You',
                content=content, color='#a78bfa',
                bg_color='rgba(108,71,255,0.2)', initials='You'
            )
            await self.channel_layer.group_send(self.room_group,
                {'type': 'chat_message', 'message': user_msg})
            await self.trigger_ai_responses(content)
        elif msg_type == 'ping':
            await self.send(json.dumps({'type': 'pong'}))

    async def chat_message(self, event):
        if self._active:
            await self.send(json.dumps({'type': 'message', 'message': event['message']}))

    async def typing_indicator(self, event):
        if self._active:
            await self.send(json.dumps({'type': 'typing', 'model': event['model']}))

    async def trigger_ai_responses(self, content):
        tags = re.findall(r'@([\w.\-]+)', content)
        models = await self.get_models()
        if not models:
            return
        if tags:
            responders = [m for m in models if any(t.lower() in m['name'].lower() for t in tags)]
            if not responders:
                responders = [random.choice(models)]
        else:
            # Only 1-2 random models respond to keep it clean
            n = random.randint(1, min(2, len(models)))
            responders = random.sample(models, n)
        # Prefer Groq models first (fastest, no rate limit issues)
        groq = [m for m in responders if m['provider'] == 'groq']
        others = [m for m in responders if m['provider'] != 'groq']
        ordered = groq + others
        for i, model in enumerate(ordered):
            asyncio.ensure_future(self.delayed_response(model, content, i * 1.5))

    async def delayed_response(self, model, user_content, delay):
        await asyncio.sleep(delay)
        if not self._active:
            return
        await self.channel_layer.group_send(self.room_group, {
            'type': 'typing_indicator',
            'model': {'name': model['name'], 'color': model['color'], 'initials': model['initials']}
        })
        await asyncio.sleep(1.2)
        if not self._active:
            return
        response = await self.call_ai_model(model, user_content)
        if response and self._active:
            ai_msg = await self.save_message(
                sender_type='ai', sender_name=model['name'],
                content=response, color=model['color'],
                bg_color=model['bg_color'], initials=model['initials'],
                model_id=model['model_id'], provider=model['provider'],
            )
            if self._active:
                await self.channel_layer.group_send(self.room_group,
                    {'type': 'chat_message', 'message': ai_msg})

    @database_sync_to_async
    def call_ai_model(self, model_data, user_content):
        try:
            from models_registry.providers import call_model
            from models_registry.models import AIModel
            from .models import Message, Room
            model_obj = AIModel.objects.filter(model_id=model_data['model_id']).first()
            if not model_obj:
                return None
            room = Room.objects.filter(slug=self.room_slug).first()
            history_msgs = []
            if room:
                recent = Message.objects.filter(room=room).order_by('-created_at')[:15]
                for m in reversed(recent):
                    role = 'user' if m.sender_type == 'user' else 'assistant'
                    history_msgs.append({'role': role, 'content': m.content})
            history_msgs.append({'role': 'user', 'content': user_content})
            system = (
                f"You are {model_obj.name} in a multi-model group chat called AI Society. "
                f"Other AI models are also in this conversation — you can @mention them by name. "
                f"Be natural, concise, and genuinely helpful. You may agree or disagree with other models. "
                f"Channel: #{self.room_slug}"
            )
            return call_model(model_obj, history_msgs, system)
        except Exception as e:
            logger.error(f"call_ai_model error [{model_data['name']}]: {e}")
            return None

    @database_sync_to_async
    def save_message(self, sender_type, sender_name, content, color, bg_color, initials,
                     model_id='', provider=''):
        from .models import Message, Room
        room, _ = Room.objects.get_or_create(slug=self.room_slug, defaults={'name': self.room_slug})
        tags = re.findall(r'@([\w.\-]+)', content)
        msg = Message.objects.create(
            room=room, sender_type=sender_type, sender_name=sender_name,
            content=content, color=color, bg_color=bg_color, initials=initials,
            model_id=model_id, provider=provider, tags=tags
        )
        return msg.to_dict()

    @database_sync_to_async
    def get_history(self):
        from .models import Message, Room
        room = Room.objects.filter(slug=self.room_slug).first()
        if not room:
            return []
        msgs = Message.objects.filter(room=room).order_by('-created_at')[:50]
        return [m.to_dict() for m in reversed(msgs)]

    @database_sync_to_async
    def get_models(self):
        from models_registry.models import AIModel
        return list(AIModel.objects.filter(is_active=True, is_free=True).values(
            'model_id', 'name', 'provider', 'color', 'bg_color', 'initials'
        ))