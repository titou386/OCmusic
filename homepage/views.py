from items.models import Item, Comment
from django.views.generic import ListView
from django.db.models import Max


class IndexView(ListView):
    template_name = "homepage/index.html"
    context_object_name = "items"
    model = Item
    paginate_by = 8

    def get_queryset(self):
        return super().get_queryset()\
            .filter(comment__in=Comment.objects.all())\
            .annotate(latest_comment=Max('comment__created_datetime'))\
            .order_by('-latest_comment')
