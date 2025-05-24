from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

# Create your models here.

class StatusdManager(models.Manager):
    def user_posts(self, user):
        return self.get_queryset().filter(author = user)

class Post(models.Model):
    class StatusProduct(models.TextChoices):
        SECOND_HAND = 'SH', 'б/у'
        NEW = 'NW', 'Новый'
    
    title = models.CharField(verbose_name="Название", max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='created')
    description = models.TextField(verbose_name="Описание")
    category = models.CharField(verbose_name="Категория", max_length=250)
    image_url = models.ImageField(verbose_name="Изображение", upload_to='barter/', blank=True, null=True)
    created  = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        verbose_name="Состояние",
        max_length=2,
        choices=StatusProduct,
        default=StatusProduct.NEW
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='barter_posts'
    )
    objects = models.Manager()
    user_posts = StatusdManager()
    
    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("barter:post_detail", 
                       args=[
                            self.created.year,
                            self.created.month,
                            self.created.day,
                            self.slug,
                        ]
        )
    

# 1.	Обмен предложениями:
# o	Создание предложения обмена:
# o	Пользователь отправляет предложение обмена, указывая:
# o	id объявления, инициирующего предложение (ad_sender_id).
# o	id объявления получателя (ad_receiver_id).
# o	Комментарий (comment).
# o	Автоматическая установка статуса предложения: «ожидает».
# o	Обновление предложения:
# o	Возможность изменения статуса предложения (например, «принята» или «отклонена»).


class ExchangeProposal(models.Model):
    class StatusOffer(models.TextChoices):
        WAIT = 'WAIT', 'Ожидает'
        ACCEPTED = "ACCEPTED", "Принято"
        CANCEL = "CANCEL", "Отклонено"

    ad_sender_id = models.ForeignKey(
        'Post',
        verbose_name="Предлагаем",
        on_delete=models.CASCADE,
        related_name='used_in_offers'
    )
    ad_receiver_id = models.ForeignKey(
        'Post',
        verbose_name="Получаем",
        on_delete=models.CASCADE,
        related_name='incoming_offers'
    )
    comment = models.TextField(verbose_name="Коментарий")
    status = models.CharField(
        verbose_name="Состояние",
        choices=StatusOffer,
        default=StatusOffer.WAIT
    )
    created_at = models.DateField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

