from django.utils import timezone
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from barter.models import Post, ExchangeProposal as Offer

@pytest.mark.django_db
def test_create_post(client):
    user = User.objects.create_user(username='testuser', password='pass')
    client.login(username='testuser', password='pass')
    url = reverse('barter:post_add')

    data = {
        'title': 'Тестовое объявление',
        'description': 'Описание товара',
        'category': 'Электроника',
        'status': 'NW',
    }

    response = client.post(url, data, follow=True)
    assert response.status_code == 200
    assert Post.objects.count() == 1
    assert Post.objects.first().title == 'Тестовое объявление'


@pytest.mark.django_db
def test_edit_post(client):
    user = User.objects.create_user(username='testuser', password='pass')
    post = Post.objects.create(
        title = 'Прошлое название',
        description = 'Описание товара',
        category = 'Электроника',
        status = 'NW',
        author = user,
        slug ='test-post',
        created = timezone.now()
    )
    
    client.login(username='testuser', password='pass')
    
    url = reverse('barter:post_edit', kwargs={
        'year': post.created.year,
        'month': post.created.month,
        'day': post.created.day,
        'post': post.slug   
    })
    
    data = {
        'title': 'Новое название',
        'description': 'Новое описание товара',
        'category': 'Электроника Б/У',
        'status': 'SH',
    }
    
    response = client.post(url, data, follow=True)
    
    assert response.status_code == 200
    
    post.refresh_from_db()
    assert post.title == 'Новое название'
    assert post.description == 'Новое описание товара'
    
    
@pytest.mark.django_db
def test_del_post(client):
    user = User.objects.create(username='testuser', password='pass')
    client.login(username='testuser', password='pass')
    
    post = Post.objects.create(
        title = 'Название для удаления',
        description = 'Описание товара для удаления',
        category = 'Удаление',
        status = 'NW',
        author = user,
        slug ='test-post',
        created = timezone.now()
    )
    
    url = reverse('barter:post_delete', kwargs={
        'pk': post.pk 
    })
    
    response = client.post(url, follow=True)
    
    assert response.status_code == 200
    assert Post.objects.filter(pk=post.pk).count() == 0

    
@pytest.mark.django_db
def test_search_post(client):
    user = User.objects.create(username='testuser', password='pass')
    client.login(username='testuser', password='pass')
    
    Post.objects.create(
        title = 'ноутбук',
        description = 'Описание ноутбука',
        category = 'Электроника',
        status = 'NW',
        author = user,
        slug ='test-post-notebook',
        created = timezone.now()
    )
    
    Post.objects.create(
        title = 'телефон',
        description = 'Описание телефона',
        category = 'Электроника',
        status = 'SH',
        author = user,
        slug ='test-post-telephone',
        created = timezone.now()
    )
    
    url = reverse('barter:home')
    
    response = client.get(url, {'search_title': 'телефон'})
    
    assert response.status_code == 200
    posts = response.context['posts']
    assert all('телефон' in post.title for post in posts)
    

@pytest.mark.django_db
def test_accept_offer(client):
    sender = User.objects.create_user(username='sender', password='pass')
    receiver = User.objects.create_user(username='receiver', password='pass')

    client.login(username='receiver', password='pass')

    sender_post = Post.objects.create(
        title='Товар отправителя',
        description='Какое-то',
        category='Электроника',
        status='NW',
        author=sender,
        slug='sender-post',
        created=timezone.now()
    )

    receiver_post = Post.objects.create(
        title='Товар получателя',
        description='Какое-то',
        category='Электроника',
        status='NW',
        author=receiver,
        slug='receiver-post',
        created=timezone.now()
    )
    
    offer = Offer.objects.create(
        ad_sender_id=sender_post,
        ad_receiver_id=receiver_post,
        status=Offer.StatusOffer.WAIT
    )

    url = reverse('barter:accept_offer', args=[offer.id])
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('barter:my_offers')

    sender_post.refresh_from_db()
    receiver_post.refresh_from_db()
    offer.refresh_from_db()
    
    assert sender_post.author == receiver
    assert receiver_post.author == sender

    assert offer.status == Offer.StatusOffer.ACCEPTED