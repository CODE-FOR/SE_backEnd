from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync

class chatConsumer(WebsocketConsumer):
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
            self.deal_send_msg(text_data_json['message'])
        if code == 700:
            self.deal_change_chat_user(text_data_json['chatuser'], text_data_json['nowuser'])

    def deal_send_msg(self, get_msg):

        msg = {}
        msg['code'] = 610
        msg['sender_id'] = 3
        msg['receiver_id'] = 2
        msg['msg'] = {
            'time': '2021-05-09',
            'send_id': 3,
            'message': get_msg
        }
        async_to_sync(self.channel_layer.group_send)(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'message': msg
            }
        )
        self.send(text_data=json.dumps(msg))

    def deal_change_chat_user(self, chatuser_id, nowuser_id):
        min_id = chatuser_id if chatuser_id < nowuser_id else nowuser_id
        max_id = chatuser_id if chatuser_id > nowuser_id else nowuser_id
        chat_group_name = str(min_id) + "_" + str(max_id)
        print(nowuser_id)
        print(chat_group_name)
        self.chat_group_name = chat_group_name
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
