from django.urls import path
from django.contrib.sitemaps.views import sitemap
from .views import (
    ArticleListView,
    ArticleView,
    ArticleExtraView,
    ArticleSearchApi,
    ArticleFeed,
)
from .sitemaps import SITEMAPS


urlpatterns = [
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": SITEMAPS},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("", ArticleExtraView.as_view(), name="about_view"),
    path("<str:slug>", ArticleExtraView.as_view(), name="menu_view"),
    path("articles/", ArticleListView.as_view(), name="articles"),
    path("articles/<int:year>/", ArticleListView.as_view(), name="articles.by_year"),
    path(
        "articles/<int:year>/<int:month>/",
        ArticleListView.as_view(),
        name="articles.by_month",
    ),
    path(
        "articles/<int:year>/<int:month>/<str:slug>",
        ArticleView.as_view(),
        name="article.detail",
    ),
    path("articles/tag/<str:tag>", ArticleListView.as_view(), name="articles.by_tag"),
    path("articles/search/", ArticleSearchApi.as_view(), name="articles.search"),
    path("articles/feed", ArticleFeed(), name="articles.feed"),
]
