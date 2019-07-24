from django.urls import reverse
from django.contrib.sitemaps import Sitemap
from .models import Article


class SblogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Article.objects.all()

    def lastmod(self, item):
        return item.updated


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return ["articles"]

    def location(self, item):
        return reverse(item)


SITEMAPS = {"dynamic": SblogSitemap, "static": StaticViewSitemap}
