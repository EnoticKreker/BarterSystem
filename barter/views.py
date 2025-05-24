from pyexpat.errors import messages
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from .forms import OfferFilterForm, OfferForm, PostFilterForm, PostForm
from .models import ExchangeProposal as Offer, Post
from django.utils.text import slugify
from transliterate import translit
from django.db.models.functions import Lower
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

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
    
    user_posts = Post.user_posts.user_posts(request.user)
    
    check_offer = Offer.objects.filter(
        ad_sender_id__in = user_posts,
        ad_receiver_id = post,
        status = Offer.StatusOffer.WAIT
    ).exists()
    
    
    return render(
        request,
        'barter/detail.html',
        {
            'post': post,
            'check_offer': check_offer,
        }
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


@login_required
def create_offer(request, post_id):
    target_post = get_object_or_404(Post, id=post_id)
    
    user_posts = Post.user_posts.user_posts(request.user)

    # Предотвращаем попытку обмена с собой
    if target_post.author == request.user:
        return redirect(target_post.get_absolute_url())
    
    
    check_offer = Offer.objects.filter(
        ad_sender_id__in = user_posts,
        ad_receiver_id = target_post,
        status = Offer.StatusOffer.WAIT
    ).first()
    
    print(check_offer)
    
    if check_offer:
        messages.warning(request, 'Вы уже отправили предложение на этот товар.')
        return redirect(target_post.get_absolute_url())

    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.ad_receiver_id = target_post
            offer.status = Offer.StatusOffer.WAIT
            offer.save()
            return redirect(target_post.get_absolute_url())
    else:
        # Отдаем только посты текущего пользователя
        form = OfferForm(user=request.user)

    return render(request, 'barter/create_offer.html', {
        'target_post': target_post,
        'form': form,
    })


@login_required
def my_offers(request):
    form = OfferFilterForm(request.GET or None)

    incoming = Offer.objects.filter(ad_receiver_id__author=request.user)
    outgoing = Offer.objects.filter(ad_sender_id__author=request.user)

    if form.is_valid():
        status = form.cleaned_data.get('status')
        if status:
            outgoing = outgoing.filter(status=status)

    return render(request, 'barter/my_offers.html', {
        'incoming': incoming,
        'outgoing': outgoing,
        'form': form,
    })


@login_required
def accept_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)

    if offer.ad_receiver_id.author != request.user:
        return redirect('barter:my_offers')

    # Передать права на post'ы:
    sender_post = offer.ad_sender_id
    receiver_post = offer.ad_receiver_id

    sender_user = sender_post.author
    receiver_user = receiver_post.author

    # 1. Пост, который отправитель предлагает (его товар), переходит получателю
    sender_post.author = receiver_user
    sender_post.save()

    # 2. Пост, который получает отправитель, переходит отправителю
    receiver_post.author = sender_user
    receiver_post.save()

    # Обновляем статус предложения
    offer.status = Offer.StatusOffer.ACCEPTED
    offer.save()
    return redirect('barter:my_offers')


@login_required
def reject_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)

    # Только отправитель или получатель может отклонить
    if request.user not in [offer.ad_receiver_id.author, offer.ad_sender_id.author]:
        return redirect('barter:my_offers')

    offer.status = Offer.StatusOffer.CANCEL
    offer.save()
    return redirect('barter:my_offers')