from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Note

User = get_user_model()


@csrf_exempt
def add_note(request):
    author = request.POST.get('author', None)
    message = request.POST.get('message', None)

    print(author, message)

    if author is None or message is None:
        return JsonResponse({'added': False, 'error_code': 'lacking_information'})

    note, created = Note.objects.get_or_create(
        author=User.objects.get(id=author), message=message)

    return JsonResponse()


@csrf_exempt
def edit_note(request, id):
    message = request.POST.get('message', None)
    print("message", message)

    if not message:
        return JsonResponse({'updated': False, 'error_code': 'Message cannot be null.'})

    if not Note.objects.filter(id=id).exists():
        return JsonResponse({'updated': False, 'error_code': 'A note with that id does not exist.'})

    note = Note.objects.get(id=id)
    note.message = message
    note.save()

    return JsonResponse()


@csrf_exempt
def resolve_note(request, id):
    if not Note.objects.filter(id=id).exists():
        return JsonResponse({'resolved': False, 'error_code': 'A note with that id does not exist.'})
    note = Note.objects.get(id=id)
    note.resolved = True
    note.save()

    return JsonResponse({'resolved': True})


def add_comment(request):
    pass


def resolve_comment(request):
    pass
