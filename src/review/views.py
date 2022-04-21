from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic import DetailView
from .forms import NewTicketForm, FollowUsersForm, NewReviewForm
from review.models import Ticket, Review
from . import models


@login_required
def home(request):
    return render(request, 'review/home.html')


@login_required
def create_ticket(request):
    form = NewTicketForm
    if request.method == 'POST':
        ticket_form = NewTicketForm(request.POST, request.FILES)
        if ticket_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('ticket_snippet', pk=ticket.id)
        else:
            print("error")

    else:
        ticket_form = NewTicketForm()

    return render(request,
                  'review/create_ticket.html',
                  {'form': form})


@login_required
def review_for_ticket(request):
    ticket_form = NewTicketForm(request.POST, request.FILES)
    review_form = NewReviewForm(request.POST)
    if ticket_form.is_valid() and review_form.is_valid():
        try:
            image = request.FILES['images']
        except MultiValueDictKeyError:
            image = None
        ticket = Ticket.objects.create(
            user=request.user,
            title=request.POST['title'],
            description=request.POST['description'],
            image=image
        )
        ticket.save()
        Review.objects.create(
            ticket=ticket,
            user=request.user,
            headline=request.POST['headline'],
            rating=request.POST['rating'],
            body=request.POST['body']
        )
        return redirect('feed')

    context = {
        'ticket_form': ticket_form,
        'review_form': review_form,
        'title': 'New Review'
    }

    return render(request, 'review/create_review.html', context)


@login_required
def review_response(request, pk):
    # ticket = get_object_or_404(Ticket, id=pk)
    ticket = Ticket.objects.get(id=pk)

    if request.method == 'POST':
        review_form = NewReviewForm(request.POST)

        if review_form.is_valid():
            Review.objects.create(
                ticket=ticket,
                user=request.user,
                headline=request.POST['headline'],
                rating=request.POST['rating'],
                body=request.POST['body']
            )
            messages.success(request, f'critique de "{ticket.title}" bien postée')
            return redirect('feed')

    else:
        review_form = NewReviewForm()

    context = {
        'form': review_form,
        'post': ticket,
        'title': 'Response Review'
    }
    return render(request, 'review/create_review.html', context)


class TicketView(DetailView):
    model = Ticket
    login_url = 'home'
    redirect_field_name = 'redirect_to'
    context_object_name = "ticket"


class ReviewView(DetailView):
    model = Review
    login_url = 'home'
    redirect_field_name = 'redirect_to'
    context_object_name = "review"


@login_required
def feed(request):
    tickets = models.Ticket.objects.all()
    return render(request, 'review/feed.html', {'tickets': tickets})


@login_required
def follow_users(request):
    form = FollowUsersForm(instance=request.user)
    user = request.user
    user_pk = request.user.id
    if request.method == 'POST':
        form = FollowUsersForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            choices = User.objects.all().exclude(pk=user_pk)
            return redirect('home')
    return render(request, 'user/follow_users_form.html', context={'form': form})


def profile_view(request):
    return render(request, 'user/profile.html')
