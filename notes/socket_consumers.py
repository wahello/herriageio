import asyncio
import json

from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

from .models import Note

User = get_user_model()


class ResolveNoteConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        """ When the socket connects. """
        self.note_socket = "resolve_event_%s" % (
            self.scope['url_route']['kwargs']['note_id'])

        await self.channel_layer.group_add(
            self.note_socket,
            self.channel_name
        )

        await self.send({
            "type": "websocket.accept",
        })

    async def websocket_receive(self, event):
        """ When the socket receives something. """
        note_id = self.scope['url_route']['kwargs']['note_id']
        note = await self.resolve_note(note_id)

        data = {
            'updated': True,
            'note_id': note_id,
            'resolved': note.resolved,
        }

        await self.channel_layer.group_send(
            self.note_socket, {
                "type": "resolve_note_event",
                'text': json.dumps(data),
            }
        )

    async def resolve_note_event(self, event):
            # adds the actual note
        await self.send({
            "type": "websocket.send",
            "text": event['text']
        })

    async def websocket_disconnect(self, event):
        """ When the socket connects. """
        print('disconnected', event)
        await self.send({
            "type": "websocket.close"
        })

    @database_sync_to_async
    def get_note(self, id_):
        return Note.objects.get(id=id_)

    @database_sync_to_async
    def resolve_note(self, id_):
        note = Note.objects.get(id=id_)
        note.resolved = True
        note.save()
        return note


class EditNoteConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        """ When the socket connects. """
        self.note_socket = "edit_note_%s" % (
            self.scope['url_route']['kwargs']['note_id'])

        await self.channel_layer.group_add(
            self.note_socket,
            self.channel_name
        )

        await self.send({
            "type": "websocket.accept",
        })

    async def websocket_receive(self, event):
        """ When the socket receives something. """
        front_text = event.get('text', None)
        if front_text is not None:
            dict_data = json.loads(front_text)

        # author = await self.get_user(dict_data['author'])
        message = dict_data['message']
        editing_user = dict_data['editing_user']
        note_id = self.scope['url_route']['kwargs']['note_id']
#
        note = await self.edit_note(note_id, message)

        data = {
            'updated': True,
            'note_id': note.id,
            'note_message': note.message,
            'edit_note_url': note.edit_note_url(),
            'resolve_note_url': note.resolve_note_url(),
            'note_author': note.author.id,
            'editing_user': editing_user,
        }

        await self.channel_layer.group_send(
            self.note_socket, {
                "type": "edit_note_event",
                'text': json.dumps(data),
            }
        )

    async def edit_note_event(self, event):
         # adds the actual note
        await self.send({
            "type": "websocket.send",
            "text": event['text']
        })

    async def websocket_disconnect(self, event):
        """ When the socket connects. """
        print('disconnected', event)
        await self.send({
            "type": "websocket.close"
        })

    @database_sync_to_async
    def get_note(self, id):
        return Note.objects.get(id=id)

    @database_sync_to_async
    def edit_note(self, id, message):
        note = Note.objects.get(id=id)
        note.message = message
        note.save()
        return note


class AddNoteConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        """ When the socket connects. """
        await self.channel_layer.group_add(
            'add_note',
            self.channel_name
        )

        await self.send({
            "type": "websocket.accept",
        })

    async def websocket_receive(self, event):
        """ When the socket receives something. """
        print('receive', event)
        front_text = event.get('text', None)
        if front_text is not None:
            dict_data = json.loads(front_text)

            try:
                author = await self.get_user(dict_data['author'])
            except:
                author = '1'

            message = dict_data['message']

            try:
                parent_id = dict_data['parent_id']
            except:
                parent_id = None

            note, created = await self.create_note(author, message, parent_id)
            author = await self.get_user(id=note.author.id)

            response = {
                'added': created,
                'note_id': note.id,
                'note_message': note.message,
                'edit_note_url': note.edit_note_url(),
                'resolve_note_url': note.resolve_note_url(),
                'note_author_name': author.username,
                'parent_id': note.parent_id,
            }

            # broadcoasts the note
            await self.channel_layer.group_send(
                'add_note',
                {
                    "type": "add_note_event",
                    "text": json.dumps(response),
                }
            )

    async def add_note_event(self, event):
        # adds the actual note
        await self.send({
            "type": "websocket.send",
            "text": event['text']
        })

    async def websocket_disconnect(self, event):
        """ When the socket connects. """
        print('disconnected', event)
        await self.send({
            "type": "websocket.close"
        })

    @database_sync_to_async
    def get_note(self, id):
        return Note.objects.get(id=id)

    @database_sync_to_async
    def create_note(self, author_obj, message, parent_id=None):
        return Note.objects.get_or_create(
            author=author_obj, message=message, parent_id=parent_id)

    @database_sync_to_async
    def get_user(self, id):
        return User.objects.get(id=id)
