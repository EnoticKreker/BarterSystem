from django import forms
from .models import ExchangeProposal as Offer, Post
from django.contrib.auth.models import User

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'category', 'image_url', 'status']
        

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['ad_sender_id', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Предлагаем только посты текущего пользователя
            self.fields['ad_sender_id'].queryset = Post.objects.filter(author=user)


class OfferFilterForm(forms.Form):
    status = forms.ChoiceField(
        required=False,
        label='Статус',
        choices=[('', 'Все статусы')] + list(Offer.StatusOffer.choices),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
            

class PostFilterForm(forms.Form):
    search_title = forms.CharField(
        required=False,
        label='Название',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поиск по названию'})
    )
    search_description = forms.CharField(
        required=False,
        label='Описание',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поиск по описанию'})
    )
    category = forms.ChoiceField(
        required=False,
        label='Категория',
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        required=False,
        label='Состояние',
        choices=[('', 'Все состояния')] + list(Post.StatusProduct.choices),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Получаем уникальные категории из базы, исключая пустые
        categories = Post.objects.values_list('category', flat=True).distinct()
        categories = [c for c in categories if c]
        choices = [('', 'Все категории')] + [(c, c) for c in categories]
        self.fields['category'].choices = choices