from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

# Create your models here.

class StatusdManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.StatusProduct.NEW)

class Post(models.Model):
    class StatusProduct(models.TextChoices):
        SECOND_HAND = 'SH', 'б/у'
        NEW = 'NW', 'Новый'
    
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='created')
    description = models.TextField()
    category = models.CharField(max_length=250)
    image_url = models.ImageField(upload_to='barter/', blank=True, null=True)
    created  = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
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
    new_products = StatusdManager()
    
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