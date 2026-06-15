import json, re, random, asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_slug = self.scope['url_route']['kwargs']['room_slug']
        self.room_group = f'chat_{self.room_slug}'
        self.is_owner = self.scope['session'].get('is_owner', False)
        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()
        # Send recent history
        history = await self.get_history()
        await self.send(json.dumps({'type': 'history', 'messages': history}))
        # Send model list
        models = await self.get_models()
        await self.send(json.dumps({'type': 'model_list', 'models': models}))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        if not self.is_owner:
            return  # Guests cannot send messages
        data = json.loads(text_data)
        msg_type = data.get('type', 'message')

        if msg_type == 'message':
            content = data.get('content', '').strip()
            if not content:
                return
            # Save user message
            user_msg = await self.save_message(
                sender_type='user', sender_name='You',
                content=content, color='#a78bfa',
                bg_color='rgba(108,71,255,0.2)', initials='You'
            )
            # Broadcast user message
            await self.channel_layer.group_send(self.room_group, {
                'type': 'chat_message', 'message': user_msg
            })
            # Parse tags and trigger AI responses
            await self.trigger_ai_responses(content)

        elif msg_type == 'ping':
            await self.send(json.dumps({'type': 'pong'}))

    async def chat_message(self, event):
        await self.send(json.dumps({'type': 'message', 'message': event['message']}))

    async def typing_indicator(self, event):
        await self.send(json.dumps({'type': 'typing', 'model': event['model']}))

    async def trigger_ai_responses(self, content):
        """Parse @mentions or pick random models to respond."""
        tags = re.findall(r'@([\w.-]+)', content)
        models = await self.get_models()

        if tags:
            responders = [m for m in models if any(t.lower() in m['name'].lower() for t in tags)]
            if not responders:
                responders = [random.choice(models)] if models else []
        else:
            n = random.randint(1, min(3, len(models)))
            responders = random.sample(models, n) if models else []

        for i, model in enumerate(responders):
            asyncio.ensure_future(self.delayed_response(model, content, i * 1.2))

    async def delayed_response(self, model, user_content, delay):
        await asyncio.sleep(delay)
        # Send typing indicator
        await self.channel_layer.group_send(self.room_group, {
            'type': 'typing_indicator',
            'model': {'name': model['name'], 'color': model['color'], 'initials': model['initials']}
        })
        await asyncio.sleep(1.5)
        # Call actual AI model
        response = await self.call_ai_model(model, user_content)
        if response:
            ai_msg = await self.save_message(
                sender_type='ai',
                sender_name=model['name'],
                content=response,
                color=model['color'],
                bg_color=model['bg_color'],
                initials=model['initials'],
                model_id=model['model_id'],
                provider=model['provider'],
            )
            await self.channel_layer.group_send(self.room_group, {
                'type': 'chat_message', 'message': ai_msg
            })

    @database_sync_to_async
    def call_ai_model(self, model_data, user_content):
        try:
            from models_registry.providers import call_model
            from models_registry.models import AIModel
            from .models import Message, Room
            model_obj = AIModel.objects.filter(model_id=model_data['model_id']).first()
            if not model_obj:
                return None
            # Get recent history for context
            room = Room.objects.filter(slug=self.room_slug).first()
            history_msgs = []
            if room:
                recent = Message.objects.filter(room=room).order_by('-created_at')[:20]
                for m in reversed(recent):
                    role = 'user' if m.sender_type == 'user' else 'assistant'
                    history_msgs.append({'role': role, 'content': m.content})
            history_msgs.append({'role': 'user', 'content': user_content})
            system = (
                f"You are {model_obj.name}, an AI model in a multi-model group chat. "
                f"Other AI models are also here. You can @mention other models by name. "
                f"Be natural, concise, and helpful. You may agree or disagree with other models. "
                f"This is channel: #{self.room_slug}"
            )
            return call_model(model_obj, history_msgs, system)
        except Exception as e:
            return f"[Error: {str(e)[:100]}]"

    @database_sync_to_async
    def save_message(self, sender_type, sender_name, content, color, bg_color, initials,
                     model_id='', provider=''):
        from .models import Message, Room
        room, _ = Room.objects.get_or_create(slug=self.room_slug, defaults={'name': self.room_slug})
        tags = re.findall(r'@([\w.-]+)', content)
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
