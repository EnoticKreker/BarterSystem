from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from .forms import PostFilterForm, PostForm
from .models import Post
from django.utils.text import slugify
from transliterate import translit
from django.db.models.functions import Lower
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

def home(request):
    form = PostFilterForm(request.GET or None)
    posts = Post.objects.all()

    if form.is_valid():
        title = form.cleaned_data.get('search_title')
        description = form.cleaned_data.get('search_description')
        category = form.cleaned_data.get('category')
        status = form.cleaned_data.get('status')

        if title:
             posts = posts.annotate(title_lower=Lower('title')).filter(title_lower__icontains=title.lower())
        if description:
            posts = posts.annotate(description_lower=Lower('description')).filter(description_lower__icontains=description.lower())
        if category:
            posts = posts.filter(category=category)
        if status:
            posts = posts.filter(status=status)
            
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page', 1)
    
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        posts = paginator.page(1)
        
    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']
    get_params_string = get_params.urlencode()

    context = {
        'form': form,
        'posts': posts,
        'get_params': get_params_string,
    }
    return render(request, 'barter/home.html', context)
    
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

class PostDeleteView(View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        return redirect('barter:home')

def product_create_or_update(request, year=None, month=None, day=None, post=None):
    if post:
        instance = get_object_or_404(
            Post, slug=post,
            created__year=year,
            created__month=month,
            created__day=day
        )
    else:
        instance = None

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            post_obj = form.save(commit=False)
            if not instance:
                trans_title = translit(post_obj.title, 'ru', reversed=True)
                post_obj.slug = slugify(trans_title)
                post_obj.author = request.user
                post_obj.created = timezone.now()
            else:
                if post_obj.title != instance.title:
                    post_obj.slug = slugify(post_obj.title, allow_unicode=True)
            post_obj.save()
            return redirect(post_obj.get_absolute_url())
    else:
        form = PostForm(instance=instance)

    return render(request, 'barter/post_form.html', {'form': form})
