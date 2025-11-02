from django.contrib import messages
from django.db.models import Q
from django.contrib.postgres.search import SearchVector
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.db.models import Avg, Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import BookRating, CreateUserForm, AuthorRatingForm, BookRatingForm, BookCommentForm
from django.contrib.auth import authenticate, login, logout
from .models import Author, Book, Featured, AuthorRating, BookRating, BookComment, Wishlist
# Create your views here.


def home(request):
    featured_book = Book.objects.order_by('-added_date').first()
    books = Book.objects.all()
    authors = Author.objects.all()
    recent = Book.objects.order_by("-added_date")
    popular = Book.objects.filter(book_rating__gt=0).order_by("-book_rating")
    context = {
        "featured_book": featured_book,
        "books": books,
        "authors": authors,
        "recent": recent,
        "popular": popular,
    }
    return render(request, 'bookreview/home.html', context)


def all_books(request):
    books = Book.objects.all()
    context = {
        "books": books,
    }
    return render(request, 'bookreview/all_books.html', context)


def book(request, id):
    book = get_object_or_404(Book, id=id)
    form = None
    comment_form = None
    is_in_wishlist = False

    if request.user.is_authenticated:
        rating_obj = BookRating.objects.filter(
            book=book, user=request.user).first()
        is_in_wishlist = Wishlist.objects.filter(
            user=request.user, book=book).exists()
        if request.method == "POST":
            form = BookRatingForm(request.POST, instance=rating_obj)
            comment_form = BookCommentForm(request.POST)

            is_rating_valid = form.is_valid()
            is_comment_valid = comment_form.is_valid()

            if is_rating_valid:
                rating = form.save(commit=False)
                rating.book = book
                rating.user = request.user
                rating.save()

            if is_comment_valid:
                comment = comment_form.save(commit=False)
                if comment.comment.strip():
                    comment.book = book
                    comment.user = request.user
                    comment.save()

            if is_rating_valid or is_comment_valid:
                return redirect('book', id=id)

        else:
            form = BookRatingForm(instance=rating_obj)
            comment_form = BookCommentForm()

    all_ratings = book.bookrating_set.exclude(
        rating=0)
    total_ratings = all_ratings.count()

    avg_rating = (
        sum(r.rating for r in all_ratings) /
        total_ratings if total_ratings > 0 else 0
    )

    all_comments = (
        BookComment.objects.filter(book=book)
        .exclude(comment__exact='')
        .order_by('-commented_at')
    )

    context = {
        "book": book,
        "form": form,
        "comment_form": comment_form,
        "all_comments": all_comments,
        "avg_rating": round(avg_rating, 1),
        "total_ratings": total_ratings,
        "user_is_authenticated": request.user.is_authenticated,
        "is_in_wishlist": is_in_wishlist,
    }
    return render(request, 'bookreview/book.html', context)


def add_wishlist(request, id):
    book = get_object_or_404(Book, id=id)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user, book=book)
    if created:
        print('Book added to wishlist')
    else:
        print("already exist")
    return redirect('book', id=id)


@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user).select_related('book')
    context = {
        'items': items,
    }
    return render(request, 'bookreview/wishlist.html', context)


@login_required
def delete_wishlist(request, id):
    book = get_object_or_404(Wishlist, id=id)
    if book.user != request.user:
        messages.error(request, "you are not able to do this")
    else:
        book.delete()
    return redirect('wishlist')


@login_required
def delete_comment(request, book_id, comment_id):
    comment = get_object_or_404(BookComment, id=comment_id, book_id=book_id)

    if comment.user != request.user:
        messages.error(
            request, "You are not authorized to delete this comment.")
    else:
        comment.delete()
        messages.success(request, "Comment deleted successfully.")

    return redirect('book', id=book_id)


def all_writers(request):
    writers = Author.objects.all()
    context = {"writers": writers}
    return render(request, 'bookreview/all_writers.html', context)


def writer(request, id):
    writer = get_object_or_404(Author, id=id)
    form = None

    if request.user.is_authenticated:
        rating_obj = AuthorRating.objects.filter(
            writer=writer, user=request.user).first()

        if request.method == "POST":
            form = AuthorRatingForm(request.POST, instance=rating_obj)
            if form.is_valid():
                rating = form.save(commit=False)
                rating.writer = writer
                rating.user = request.user
                rating.save()
                return redirect('writer', id=writer.id)
        else:
            form = AuthorRatingForm(instance=rating_obj)

    all_ratings = writer.authorrating_set.exclude(rating=0)
    total_ratings = all_ratings.count()
    avg_rating = (
        sum(r.rating for r in all_ratings) /
        total_ratings if total_ratings > 0 else 0
    )

    context = {
        "writer": writer,
        "form": form,
        "avg_rating": round(avg_rating, 1),
        "total_ratings": total_ratings,
        "user_is_authenticated": request.user.is_authenticated,
    }
    return render(request, 'bookreview/writer.html', context)


def discover(request):
    query = request.GET.get('q', '').strip()
    book_results = []
    writer_results = []

    if query:
        book_results = Book.objects.filter(title__icontains=query)
        writer_results = Author.objects.filter(name__icontains=query)

    context = {
        "query": query,
        "book_results": book_results,
        "writer_results": writer_results,
    }
    return render(request, "bookreview/discover.html", context)


def registration(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    context = {'form': form}
    return render(request, 'bookreview/registration.html', context)


def loginPage(request):
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
    context = {'next': request.GET.get('next'), 'error': error, }
    return render(request, 'bookreview/login.html', context)


def logoutPage(request):
    logout(request)
    return redirect('home')
