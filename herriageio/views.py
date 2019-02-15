from django.shortcuts import get_object_or_404, render, redirect, render_to_response


def home(request):
    template_name = "herriageio/home.html"
    context = {}

    return render(request, template_name, context)
