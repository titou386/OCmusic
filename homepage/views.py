from items.models import Item, Comment
from .models import ContactForm
from django.views.generic import ListView, CreateView
from django.db.models import Max
from django.urls import reverse_lazy


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


class SaveContactFormView(CreateView):
    model = ContactForm
    fields = ['name', 'email', 'phone', 'message']
    http_method_names = ['post']
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.ip = '127.0.0.1'
        return super().form_valid(form)

#    def post(self, request, *args, **kwargs):
#        self.object = self.get_object()
#        context = self.get_context_data(object=self.object)
#        return super().post(request, *args, **kwargs)

