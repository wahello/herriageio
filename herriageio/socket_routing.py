from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from django.urls import path

from notes.socket_consumers import AddNoteConsumer, EditNoteConsumer, ResolveNoteConsumer

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    path("notes/add_note/", AddNoteConsumer),
                    path("notes/edit_note/<note_id>/", EditNoteConsumer),
                    path("notes/resolve_note/<note_id>/", ResolveNoteConsumer),
                ]
            )
        )
    )})
