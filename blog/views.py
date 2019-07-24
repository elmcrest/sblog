from django.http import Http404, JsonResponse
from django.urls import reverse
from django.db.models import Q
from django.utils.html import format_html, mark_safe
from django.views.generic import View, ListView, DetailView
from django.contrib.syndication.views import Feed

from content_editor.renderer import PluginRenderer
from content_editor.contents import contents_for_item
from taggit.models import Tag

from .models import Article, RichText, Download, Image

renderer = PluginRenderer()
renderer.register(RichText, lambda plugin: mark_safe(plugin.text))
renderer.register(
    Download,
    lambda plugin: format_html(f"<a href='{plugin.file.url}'>{plugin.file.name}</a>"),
)
renderer.register(
    Image,
    lambda plugin: format_html(f"<img src='{plugin.image.url}' alt='{plugin.alt}'/>"),
)


class ArticleListView(ListView):
    """ Article ListView with optional filtering by year or year and month or tag """

    model = Article

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            all_tags=Tag.objects.order_by("name").all(), **kwargs
        )

    def get_queryset(self):
        kwargs = self.kwargs
        queryset = Article.objects.exclude(in_menu=True).prefetch_related("tags")
        if kwargs.get("year", False):
            return queryset.filter(created__year=kwargs["year"])
        elif kwargs.get("month", False):
            return queryset.filter(
                created__year=kwargs["year"], created__month=kwargs["month"]
            )
        elif kwargs.get("tag", False):
            return queryset.filter(tags__name__in=[kwargs["tag"]])
        else:
            return queryset.all()

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ArticleView(DetailView):
    """ Article View which excludes "in-menu" items. """

    model = Article

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            content=contents_for_item(
                self.object, [RichText, Download, Image]
            ).render_regions(renderer),
            related=Article.objects.exclude(id=self.object.id)
            .exclude(in_menu=True)
            .order_by("created")[:5],
            **kwargs,
        )

    def get_object(self, queryset=None):
        try:
            return (
                Article.objects.filter(created__year=self.kwargs["year"])
                .filter(created__month=self.kwargs["month"])
                .get(slug=self.kwargs["slug"])
            )
        except Article.DoesNotExist:
            raise Http404("No Article matches the given query.")


class ArticleExtraView(ArticleView):
    """ A different View to the same model to get some nicer URL for "in-menu" intems """

    def get_object(self, queryset=None):
        kwargs = self.kwargs
        try:
            if kwargs.get("slug", False):
                return Article.objects.order_by("updated").get(slug=kwargs["slug"])
            else:
                # return home view, which is by convention the article with headline "about"
                return Article.objects.get(slug="about")
        except Article.DoesNotExist:
            raise Http404("No Article matches the given query.")


class ArticleSearchApi(View):
    """ Api Endpoint for async search requests from client """

    def get(self, request):
        """ returns found articles or nothing """
        query = Article.objects.exclude(in_menu=True)

        article_filter = Q()
        searchable_paths = {}

        search_terms = [term for term in request.GET.get("query").split(" ")]
        for term in search_terms:
            searchable_paths[term] = Q(headline__icontains=term) | Q(
                teaser__icontains=term
            )

        for key in searchable_paths.keys():
            article_filter &= searchable_paths[key]

        query = query.filter(article_filter).distinct()
        articles = [
            {
                "updated": article.updated,
                "headline": article.headline,
                "teaser": article.teaser,
                "tags": [tag.name for tag in article.tags.all()],
                "url": reverse(
                    "article.detail",
                    kwargs={
                        "year": article.created.year,
                        "month": article.created.month,
                        "slug": article.slug,
                    },
                ),
            }
            for article in query
        ]

        return JsonResponse({"articles": articles})


class ArticleFeed(Feed):
    title = "raesener.de Artikel Feed"
    link = "/feed/"
    description = "RSS bzw. Atom Feed zu meinen Artikeln."

    def items(self):
        return Article.objects.exclude(in_menu=True).all()

    def item_title(self, item):
        return item.headline

    def item_description(self, item):
        return item.teaser

