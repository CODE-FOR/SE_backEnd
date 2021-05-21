from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync


class ChatConsumer(WebsocketConsumer):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(args, kwargs)
    #     self.chat_group_name = set()

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
            self.deal_create_groups(text_data_json['user_id'], text_data_json['chat_list'])

    def deal_send_msg(self, get_msg):
        sender_id = get_msg['sender_id']
        receiver_id = get_msg['receiver_id']
        min_id = sender_id if sender_id < receiver_id else receiver_id
        max_id = sender_id if sender_id > receiver_id else receiver_id
        chat_group_name = str(min_id) + "_" + str(max_id)
        async_to_sync(self.channel_layer.group_send)(
            chat_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'sender_id': sender_id,
                    'receiver_id': receiver_id,
                    'msg': {
                        'message': get_msg['msg']['message'],
                        'time': get_msg['msg']['time'],
                        'send_id': sender_id,
                        'to_id': receiver_id
                    },
                    'code': 610
                }
            }
        )
        # self.send(text_data=json.dumps(msg))

    """Group name meanings
    
    user_id: 
            As a group name, it means all the channels held by the same user
            is in a common group.
            It's used to tell the user, someone is trying to chat with you.
            Should use this when A try to chat with B,
            should first use user_id to tell B that A is trying to chat with B.
            That's for when B' chat user list does not include A,
            should add A to B's chat user list.
            After B get this notification, B should send a socket message,
            telling the backend it got A, and backend add B with group A_B.
            (And A should already has this one).
            
    min_id_max_id:
            For point to point chat.
            A want to chat with B,
            A & B should in A_B.
            When first connect, the front end should send a socket message
            to tell who is in the current_user's chat user list.
    """
    # TODO: the message may lost when A send message to B, when B's chat user list does not include A.
    def deal_create_groups(self, user_id, chat_list):
        async_to_sync(self.channel_layer.group_add)(
            str(user_id),
            self.channel_name
        )
        for chat_id in chat_list:
            min_id = user_id if user_id < chat_id else chat_id
            max_id = user_id if user_id > chat_id else chat_id
            chat_group_name = str(min_id) + "_" + str(max_id)
            # self.chat_group_name.add(chat_group_name)
            print(chat_id)
            print(chat_group_name)
            async_to_sync(self.channel_layer.group_add)(
                chat_group_name,
                self.channel_name
            )

    def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
