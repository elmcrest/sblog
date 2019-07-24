from django import forms
from django.contrib import admin
from django.db import models
from content_editor.admin import ContentEditor, ContentEditorInline

from .models import Article, RichText, Image, Download, Image


class RichTextArea(forms.Textarea):
    def __init__(self, attrs=None):
        # provides a class for plugin_ckeditor.js
        default_attrs = {"class": "richtext"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class RichTextInline(ContentEditorInline):
    model = RichText
    formfield_overrides = {models.TextField: {"widget": RichTextArea}}
    regions = ["main"]


@admin.register(Article)
class ArticleAdmin(ContentEditor, admin.ModelAdmin):
    prepopulated_fields = {"slug": ("headline",)}
    inlines = [
        RichTextInline,
        ContentEditorInline.create(model=Image),
        ContentEditorInline.create(model=Download),
    ]

    class Media:
        js = ("//cdn.ckeditor.com/4.5.6/standard/ckeditor.js", "app/plugin_ckeditor.js")
