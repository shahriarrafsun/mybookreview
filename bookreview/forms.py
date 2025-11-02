from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import AuthorRating, BookRating, BookComment, Wishlist


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class AuthorRatingForm(forms.ModelForm):
    class Meta:
        model = AuthorRating
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5})
        }


class BookRatingForm(forms.ModelForm):
    class Meta:
        model = BookRating
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5})
        }


class BookCommentForm(forms.ModelForm):
    class Meta:
        model = BookComment
        fields = ['comment']


class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ['book']
