from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from .forms import PostForm
from .models import Post
from django.utils.text import slugify

# Create your views here.

def home(request):
    posts_list = Post.objects.all()

    return render(
        request,
        'barter/home.html',
        {'posts': posts_list}
    )
    
def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        slug = post,
        created__year = year,
        created__month = month,
        created__day = day
    )
    return render(
        request,
        'barter/detail.html',
        {'post': post}
    )

def product_create_or_update(request, year=None, month=None, day=None, post=None):
    if post:  # редактирование
        instance = get_object_or_404(
            Post, slug=post,
            created__year=year,
            created__month=month,
            created__day=day
        )
    else:  # создание
        instance = None

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            post_obj = form.save(commit=False)
            if not instance:
                post_obj.slug = slugify(post_obj.title)
                post_obj.author = request.user
                post_obj.created = timezone.now()
            post_obj.save()
            return redirect(post_obj.get_absolute_url())
    else:
        form = PostForm(instance=instance)

    return render(request, 'barter/post_form.html', {'form': form})
