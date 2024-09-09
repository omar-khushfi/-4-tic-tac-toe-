import json
import re
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class GameConsumer(WebsocketConsumer):
    room_users = {}  # متغير لتخزين عدد المستخدمين في الغرفة

    def connect(self):
        self.room_name = re.sub(r'\s+', '-', self.scope['url_route']['kwargs']['room_name'])
        self.group_name = f"game_{self.room_name}"
        if self.group_name not in GameConsumer.room_users:
            GameConsumer.room_users[self.group_name] = 0

        # زيادة عدد المستخدمين المتصلين بالغرفة
        GameConsumer.room_users[self.group_name] += 1

        print(f"Connected users in {self.group_name}: { GameConsumer.room_users[self.group_name]}")
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

        # إرسال عدد المستخدمين إلى جميع الموجودين في الغرفة
        async_to_sync(self.channel_layer.group_send)(
            self.group_name, 
            {
                'type': 'update_users',
                'connected_users':  GameConsumer.room_users[self.group_name]
            }
        )

    def disconnect(self, close_code):
        
        GameConsumer.room_users[self.group_name] -= 1
        
        print(f"Connected users in {self.group_name}: { GameConsumer.room_users[self.group_name]}") 
        
        from app.models import Game, User

        user_id = self.scope['user'].id  # الحصول على معرف المستخدم
        try:
            user = User.objects.get(id=user_id)
            
            # الحصول على اللعبة باستخدام معرف الغرفة (والذي هو معرف اللعبة)
            game = Game.objects.get(id=self.scope['url_route']['kwargs']['room_name'])  # room_name هنا هو معرف اللعبة
            
            # إزالة المستخدم من اللعبة
            game.player.remove(user)
            game.save()
            
        except User.DoesNotExist:
            print(f"User with id {user_id} does not exist.")
        except Game.DoesNotExist:
            print(f"Game with id {self.scope['url_route']['kwargs']['room_name']} does not exist.")
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name,  # استخدام self.group_name
                self.channel_name
            )

        # إرسال عدد المستخدمين المحدث إلى جميع الموجودين في الغرفة
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,  # استخدام self.group_name
            {
                'type': 'update_users',
                'connected_users':GameConsumer.room_users[self.group_name]
            }
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        x = text_data_json['x']
        game_id = text_data_json['game']
        user_id = text_data_json['user']

        from app.models import Game, User, Move

        try:
            user = User.objects.get(id=user_id)
            game = Game.objects.get(id=game_id)
        except User.DoesNotExist:
            self.send(text_data=json.dumps({
                'error': f"User with id {user_id} does not exist."
            }))
            return
        except Game.DoesNotExist:
            self.send(text_data=json.dumps({
                'error': f"Room with id {game_id} does not exist."
            }))
            return

        new_move = 'x'
        if game.currnt_move == 'x':
            new_move ='o'
        else:
            'x'
        game.currnt_move = new_move
        game.save()

        move = Move.objects.create(x=x, game=game, ty=new_move)

        # إرسال التحديث لجميع المستخدمين في الغرفة
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,  # تم التعديل هنا
            {
                'type': 'game_move',
                'x': x,
                'user': user.username,
                'currnt_move': new_move,
            }
        )

    def game_move(self, event):
        x = event['x']
        user = event['user']
        currnt_move = event['currnt_move']
        div = 'cell' + str(x)

        # إرسال البيانات إلى WebSocket
        self.send(text_data=json.dumps({
            'type': 'move',
            'x': x,
            'user': user,
            'currnt_move': currnt_move,
            'd': div
        }))

    # التعامل مع إرسال عدد المستخدمين
    def update_users(self, event):
        connected_users = event['connected_users']

        # إرسال عدد المستخدمين الحاليين إلى WebSocket
        self.send(text_data=json.dumps({
            'type': 'user_count',
            'connected_users': connected_users
        }))
