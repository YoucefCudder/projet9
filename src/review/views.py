from itertools import chain
from django.db.models import CharField, Value
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic import DetailView
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

    # combine and sort the two types of posts
    posts = sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )

    return render(request, 'review/home.html', context={'posts': posts, 'followed_users': followed_users})


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
    login_url = 'home'
    redirect_field_name = 'redirect_to'
    context_object_name = "review"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['review'] = Review.objects.all()
        context['ticket'] = Ticket.objects.all()
        return context


class TicketView(DetailView):
    model = Ticket

    def get_context_data(self, **kwargs):
        context = super(TicketView, self).get_context_data(**kwargs)
        context['review'] = Review.objects.all()

        return context


@login_required
def review_detail(request, pk):
    review = Review.objects.get(id=pk)
    followed_users = get_user_follows(request.user)

    context = {
        'post': review,
        'title': 'Review detail',
        'followed_users': followed_users
    }

    return render(request, 'reviews/post_detail.html', context)


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
    return render(request, 'review/feed.html')


@login_required()
def update_ticket(request, pk):
    ticket_to_update = Ticket.objects.get(pk=pk)
    form = NewTicketForm(instance=ticket_to_update)
    if request.method == 'POST':
        form = NewTicketForm(request.POST, request.FILES, instance=ticket_to_update)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            image = form.cleaned_data['image']
            Ticket(title=title, description=description, image=image).save()
            return redirect('feed')
    return render(request, 'review/update_ticket.html', {'form': form})


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
