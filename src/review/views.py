from itertools import chain
from django.db.models import CharField, Value
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, DeleteView
from .models import Ticket, Review, UserFollows
from .forms import NewTicketForm, FollowUsersForm, NewReviewForm
from django.core.exceptions import ObjectDoesNotExist


@login_required
def home(request):
    followed_users = get_user_follows(request.user)

    # feed = Ticket.objects.filter(ticket__in=request.user.following.all())
    reviews = get_users_viewable_reviews(request.user)
    # returns queryset of reviews
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = get_users_viewable_tickets(request.user)
    # returns queryset of tickets
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))
    replied_tickets = get_replied_tickets(tickets=tickets)
    # combine and sort the two types of posts
    posts = sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )
    return render(request, 'review/home.html', context={'posts': posts, 'followed_users': followed_users,
                                                        'replied': replied_tickets})


def get_user_follows(request):
    follows = UserFollows.objects.filter(user=request)
    followed_users = []
    for follow in follows:
        followed_users.append(follow.followed_user)

    return followed_users


def get_users_viewable_reviews(user):
    followed_users = get_user_follows(user)
    followed_users.append(user)
    reviews = Review.objects.filter(user__in=followed_users)

    return reviews


def get_users_viewable_tickets(user):
    followed_users = get_user_follows(user)
    followed_users.append(user)
    tickets = Ticket.objects.filter(user__in=followed_users)
    return tickets


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
        NewTicketForm()

    return render(request,
                  'review/create_ticket.html',
                  {'form': form})


@login_required
def review_with_ticket(request):
    ticket_form = NewTicketForm(request.POST, request.FILES)
    review_form = NewReviewForm(request.POST)
    if ticket_form.is_valid() and review_form.is_valid():
        try:
            print(request.FILES)
            image = request.FILES['image']
        except MultiValueDictKeyError:
            image = None
        ticket = Ticket.objects.create(
            user=request.user,
            title=request.POST['title'],
            description=request.POST['description'],
            image=image
        )
        ticket.save()
        review = Review.objects.create(
            ticket=ticket,
            user=request.user,
            headline=request.POST['headline'],
            rating=request.POST['rating'],
            body=request.POST['body']
        )
        review.save()
        return redirect('feed')

    context = {
        'ticket_form': ticket_form,
        'review_form': review_form,
        'title': 'New Review'
    }

    return render(request, 'review/create_review.html', context)


@login_required
def review_response(request, pk):
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


class ReviewView(DetailView):
    model = Review

    def get_context_data(self, *args, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['ticket'] = Ticket.objects.filter(*args)
        context['post'] = Review.objects.filter(*args)

        return context


class TicketView(DetailView):
    model = Ticket

    def get_context_data(self, *args, **kwargs):
        context = super(TicketView, self).get_context_data(**kwargs)
        context['review'] = Review.objects.filter(*args)
        context['post'] = Ticket.objects.filter(*args)

        context['replied'] = get_replied_tickets(tickets=context['post'])
        return context


def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    context = {
        'post': ticket,
        'title': 'Ticket detail'

    }

    return render(request, 'review/post.html', context)


def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    context = {
        'post': review,
        'title': 'Review detail'
    }

    return render(request, 'review/post.html', context)


def get_replied_tickets(tickets):
    replied_tickets = []
    for ticket in tickets:
        try:
            replied = Review.objects.get(ticket=ticket)
            if replied:
                replied_tickets.append(replied.ticket)
        except ObjectDoesNotExist:
            pass
    return replied_tickets


@login_required
def feed(request):
    tickets = Ticket.objects.all()
    return render(request, 'review/feed.html', {'tickets': tickets})


def profile_view(request):
    return render(request, 'user/profile.html')


def delete_ticket(request, pk):
    ticket_to_delete = Ticket.objects.get(pk)
    if ticket_to_delete:
        ticket_to_delete.delete()
    return render(request, 'review/confirm_delete_ticket.html')


class DeleteTicketView(DeleteView):
    model = Ticket
    template_name = "review/confirm_delete_ticket.html"
    success_url = reverse_lazy("home")


@method_decorator(login_required, name='dispatch')
class DeleteReviewView(DeleteView):
    model = Review
    context_object_name = 'review'
    template_name = "review/confirm_delete_review.html"
    success_url = reverse_lazy("home")

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.object = self.get_object()

    def test_func(self):
        return self.object.user == self.request.user


def delete_review(request, pk):
    review_to_delete = Review.objects.filter(pk)
    if review_to_delete:
        review_to_delete.delete()
    return render(request, 'review/feed.html')


@login_required()
def update_ticket(request, pk):
    ticket_to_update = Ticket.objects.get(pk=pk)
    form = NewTicketForm(instance=ticket_to_update)
    if request.method == 'POST':
        form = NewTicketForm(request.POST, request.FILES, instance=ticket_to_update)
        if form.is_valid():
            form.save()
            return redirect('feed')
    return render(request, 'review/update_ticket.html', {'form': form})


@login_required()
def update_review(request, pk):
    review_to_update = Review.objects.get(pk=pk)
    review_form = NewReviewForm(instance=review_to_update)
    if request.method == 'POST':
        review_form = NewReviewForm(request.POST, instance=review_to_update)
        if review_form.is_valid():
            review_form.save()
            return redirect('home')
    return render(request, 'review/update_review.html', {'review_form': review_form})


@login_required
def follow_users(request):
    if request.method == 'POST':
        form = FollowUsersForm(request.POST)
        if form.is_valid():
            try:
                followed_user = User.objects.get(username=request.POST['followed_user'])
                if request.user == followed_user:
                    messages.error(request, 'vous ne pouvez pas vous abonner à votre compte')
                else:
                    try:
                        UserFollows.objects.create(user=request.user, followed_user=followed_user)
                        messages.success(request, f'You êtes désormais abonné  à {followed_user}!')
                    except IntegrityError:
                        messages.error(request, f'Vous êtes déjà abonné à {followed_user}!')
            except ObjectDoesNotExist:
                messages.error(request, f' {form.data["followed_user"]} does not exist.')
    else:
        form = FollowUsersForm()

    user_follows = UserFollows.objects.filter(user=request.user).order_by('followed_user')
    followed_by = UserFollows.objects.filter(followed_user=request.user).order_by('user')
    context = {
        'form': form,
        'user_follows': user_follows,
        'followed_by': followed_by,
        'title': 'Abonnements',
    }
    return render(request, 'user/follow_users_form.html', context)
