from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
# Create your views here.
from django.views import View
from django.contrib import messages
from django.core import serializers
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .forms import *

import pandas as pd
import json

def sendProcess(request,message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'private_' + str(request.user.id),
        {
            "type": "send_process",
            "message": message,
            "location" : location
        }
    )

class NoteDashboardDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        notes = Note.objects.filter(user = request.user)
        context = {
                    "notes" : notes
            }
        return render(request, 'note/note_dashboard.html', context)
    
class NoteAddExView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Request")
        form = NoteForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "form" : form
        }
        return render(request, 'note/note_add.html', context)
    
    def post(self, request, *args, **kwargs):
        form = NoteForm(request.POST, request.FILES or None)
        if form.is_valid():
            note = form.save(commit = False)
            note.user = request.user
            note.save()
            return HttpResponse(status=204)
        else:
            print(form.errors)
            context = {
                    "form" : form
            }
            return render(request, 'note/note_add.html', context)

class NoteAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Note")
        
        newNote = Note.objects.create(
            title = request.GET.get("title"),
            text  =request.GET.get("text"),
            user = request.user
        )
        
        newNote.save()
        
        
        note = {
            "id" : newNote.id,
            "title" : newNote.title,
            "text" : newNote.text,
            "date" : newNote.created_date.strftime("%d.%m.%Y")
        }
        
        sendProcess(request,note,"note_add")
        
        context = {
                "tag": tag
        }
        return HttpResponse(status=204)

class NoteDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Delete Note")
        
        exNote = Note.objects.select_related().filter(id = int(request.GET.get("note"))).first()
        exNoteId = exNote.id
        note = {
            "id" : exNoteId
        }
        
        exNote.delete()
        
        sendProcess(request,note,"note_delete")
        
        context = {
                "tag": tag
        }
        return HttpResponse(status=204)


class NoteUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Update Note")
        notes = Note.objects.filter()
        note = get_object_or_404(Note, id = id)
        form = NoteForm(request.POST or None, request.FILES or None, instance = note)
        context = {
                "tag": tag,
                "form" : form,
                "notes" : notes,
                "note" : note
         }
        return render(request, 'note/note_add.html', context)
    
    def post(self, request, id, *args, **kwargs):
        note = get_object_or_404(Note, id = id)
        form = NoteForm(request.POST, request.FILES or None, instance = note)
        if form.is_valid():
            note = form.save(commit = False)
            note.user = request.user
            note.save()
            return HttpResponse(status=204)
        else:
            context = {
                     "form" : form
             }
            return render(request, 'note/note_add.html', context)