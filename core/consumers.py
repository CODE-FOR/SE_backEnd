from channels.generic.websocket import WebsocketConsumer
import json
from time import sleep

class chatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        # message  =text_data_json['message']
        code = text_data_json['code']
        print(code)
        print(text_data_json)
        if code == 600:
            self.deal_send_msg(text_data_json['message'])

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
        self.send(text_data=json.dumps(msg))
