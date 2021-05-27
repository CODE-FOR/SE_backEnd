from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync
from core.models.chat import add_chat_list_or_update_it
from core.api.chat import add_chat_message
from core.models.user import User

class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_user_list = set()
        self.user_id = 0

    def connect(self):
        self.accept()

    def disconnect(self, code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        print(text_data)
        text_data_json = json.loads(text_data)
        # message  =text_data_json['message']
        code = text_data_json['code']
        print(code)
        print(text_data_json)
        if code == 600:
            self.deal_send_msg(text_data_json)
        if code == 700:
            self.deal_create_group(text_data_json['user_id'])

    """ Send to group(str(receiver_id)) is not difficult to understand
        Send to group(str(sender_id)) is for there are several channels in sender_id,
            the message send out should be in every channel.
            To notify those channels, should send to group(str(sender_id))
            Need to judge whether sender_id and receiver_id is the same id,
            otherwise message will be send twice.
    """
    def deal_send_msg(self, get_msg):
        code = get_msg['code']
        sender_id = get_msg['sender_id']
        receiver_id = get_msg['receiver_id']
        if code == 600:
            u = User.objects.filter(id=receiver_id).first()
            t = User.objects.filter(id=sender_id).first()
            add_chat_list_or_update_it(u, t)

        c_time = add_chat_message(sender_id, receiver_id, get_msg['msg']['message']).strftime('%Y-%m-%d %H:%M:%S')

        send_data = {
            'type': 'chat_message',
            'message': {
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'msg': {
                    'message': get_msg['msg']['message'],
                    # 'time': get_msg['msg']['time'],
                    'time': c_time,
                    'send_id': sender_id,
                    'to_id': receiver_id
                },
                'code': 610
            }
        }
        if not sender_id == receiver_id:
            async_to_sync(self.channel_layer.group_send)(
                str(sender_id),
                send_data
            )
        async_to_sync(self.channel_layer.group_send)(
            str(receiver_id),
            send_data
        )

    """ For channels send message does not need channels in group
        So We can simply use user_id as one's group name.
        Send Message:
                     Find receiver_id, send message to group(str(receiver_id))
        Do not need add_new_chat_user function.
    """

    def deal_create_group(self, user_id):
        self.user_id = user_id
        async_to_sync(self.channel_layer.group_add)(
            str(user_id),
            self.channel_name
        )

    def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

    def websocket_disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            str(self.user_id),
            self.channel_name
        )
