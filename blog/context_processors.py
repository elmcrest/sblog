from django.contrib.sites.models import Site
from .models import Article


def build_menu():
    menu = list()
    articles = Article.objects.filter(in_menu=True).order_by("menu_order")
    for article in articles:
        menu.append(article)
    return [
        "ArticleListView"
    ] + menu  # add pseudo element to list to add a static link in Template


current_site = Site.objects.get_current()


def sblog_global_context(request, domain=current_site.domain, menu=build_menu):
    return {"site": f"{domain}", "menu": menu()}
