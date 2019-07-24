from django.utils.translation import gettext_lazy as _
from django.db import models

from content_editor.models import Template, Region, create_plugin_base
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from taggit.managers import TaggableManager


# class Image(models.Model):
#     image = models.ImageField(upload_to="original_images")
#     main_image = ImageSpecField(
#         source="image",
#         processors=[ResizeToFill(100, 50)],
#         format="JPEG",
#         options={"quality": 60},
#     )
#     caption = models.CharField(_("_caption"), max_length=200)


class Article(models.Model):
    created = models.DateTimeField(_("_created"), auto_now_add=True)
    updated = models.DateTimeField(_("_updated"), auto_now=True)
    headline = models.CharField(_("_headline"), max_length=200)
    teaser = models.TextField(_("_teaser"))
    slug = models.SlugField(_("_slug"), max_length=200)
    in_menu = models.BooleanField(_("_in_menu"), default=False)
    menu_order = models.IntegerField(_("_menu_order"), null=True, blank=True)

    tags = TaggableManager(blank=True)

    regions = [
        Region(key="main", title="main region"),
        Region(key="sidebar", title="sidebar region", inherited=False),
    ]

    class Meta:
        unique_together = (("slug", "created"),)
        ordering = ["-updated"]

    def get_absolute_url(self):
        if self.slug == "about":
            return "/"
        elif self.in_menu:
            return f"/{self.slug}"
        else:
            return f"/articles/{self.created.year}/{self.created.month}/{self.slug}"

    def get_unique_identifier(self):
        return f"{self.created.year}_{self.created.month}_{self.slug}"

    def __str__(self):
        return self.headline


ArticlePlugin = create_plugin_base(Article)


class RichText(ArticlePlugin):
    text = models.TextField(blank=True)

    class Meta:
        verbose_name = _("_richtext")
        verbose_name_plural = _("_richtexts")


class Image(ArticlePlugin):
    image = models.ImageField(upload_to="images/%Y/%m")
    alt = models.CharField(max_length=200)

    class Meta:
        verbose_name = _("_image")
        verbose_name_plural = _("_images")


class Download(ArticlePlugin):
    file = models.FileField(upload_to="download/%Y/%m")

    class Meta:
        verbose_name = _("_downloaditem")
        verbose_name_plural = _("_downloaditems")
