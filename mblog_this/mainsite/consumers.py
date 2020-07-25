import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

import logging

common_log = logging.getLogger('django')


class InformConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'yunbo_inform'

        # 将用户加进组里
        await self.channel_layer.group_add(  # 所用的通道方法都必须是异步方法
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        # 将用户移除组
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # async def receive(self, text_data=None, bytes_data=None, **kwargs):
    #     text_data_json = json.loads(text_data)
    #     message = text_data_json['message']
    #
    #     # 群发出去
    #     await self.channel_layer.group_send(
    #         self.group_name,
    #         # 事件
    #         {
    #             'type': 'web_update_inform',  # 事件名
    #             'message': message
    #         }
    #     )

    async def web_update_inform(self, event):
        """文章更新消息发送"""
        await self.send(text_data=json.dumps(event))

    async def homework_inform(self, event):
        """交作业消息发送"""
        await self.send(text_data=json.dumps(event))


def send_inform(func, username, article, slug, head_image=None, trigger_username=None, group_name=None):
    """从外部发送消息到channels，文章更新"""

    if group_name is None:
        group_name = 'yunbo_inform'

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            # 事件跟随组名
            'type': 'web_update_inform',
            'func': func,
            'username': username,
            'article': article,
            'slug': slug,
            'head_image': head_image,
            'trigger_username': trigger_username
        }
    )


def inform_handleHomework(func, article, name, project, group_name=None):
    """发送作业成功网站广播"""

    if group_name is None:
        group_name = 'yunbo_inform'

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'homework_inform',
            'func': func,
            'name': name,
            'article': article,
            'project': project
        }
    )
