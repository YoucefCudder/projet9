from django import forms
from django.forms import ImageField, RadioSelect
from . import models


class NewTicketForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        fields = ['title', 'description', 'image']
        widget = {"image": ImageField()}


class NewReviewForm(forms.ModelForm):
    headline = forms.CharField(
        label="Title",
        max_length=128,
        widget=forms.TextInput()
    )
    rating = forms.ChoiceField(
        initial=1,
        label="Rating",
        widget=RadioSelect(),
        choices=((1, "1 étoiles"), (2, "2 étoiles"),
                 (3, "3 étoiles"), (4, "4 étoiles"), (5, '5 étoiles'))
    )
    body = forms.CharField(
        label="Review",
        max_length=8192,
        widget=forms.Textarea(),
        required=False
    )

    class Meta:
        model = models.Review
        fields = ['headline', 'rating', 'body']


class FollowUsersForm(forms.Form):
    followed_user = forms.CharField(
        label=False,
        widget=forms.TextInput()
    )
