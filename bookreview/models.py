from django.db import models
from datetime import date
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.


class Author(models.Model):
    name = models.CharField(max_length=200)
    birth_year = models.DateField(blank=True, null=True)
    death_year = models.DateField(blank=True, null=True)
    about = models.TextField()
    author_rating = models.FloatField(default=0.0)
    dp = models.ImageField(upload_to='author_dp/', blank=True, null=True)
    author_rating_count = models.IntegerField(default=0)

    def lifespan(self):
        if self.birth_year and self.death_year:
            return f"{self.birth_year.year}-{self.death_year.year}"
        elif self.birth_year and not self.death_year:
            return f"{self.birth_year.year}-present"
        elif not self.birth_year and not self.death_year:
            return "N/A"

    def __str__(self):
        return self.name


class AuthorRating(models.Model):
    writer = models.ForeignKey(
        Author, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    rated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('writer', 'user')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.writer:
            all_ratings = self.writer.authorrating_set.all()
            avg = sum(r.rating for r in all_ratings) / len(all_ratings)
            self.writer.author_rating = round(avg, 2)
            self.writer.author_rating_count = len(all_ratings)
            self.writer.save()

    def __str__(self):
        return f"{self.user.username} rated {self.writer.name}: {self.rating}"


class Book(models.Model):
    writer = models.ForeignKey(
        Author, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=200)
    cover = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    published_date = models.DateField(
        default=timezone.now, blank=True, null=True)
    added_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True, default="N/A")
    book_rating = models.FloatField(default=0.0)
    book_rating_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Wishlist(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, blank=True, null=True)
    add_date = models.DateTimeField(auto_now_add=True)


class BookRating(models.Model):
    book = models.ForeignKey(
        Book, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    rated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('book', 'user')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.book:
            all_ratings = self.book.bookrating_set.all()
            avg = sum(r.rating for r in all_ratings)/len(all_ratings)
            self.book.book_rating = round(avg, 2)
            self.book.book_rating_count = len(all_ratings)
            self.book.save()

    def __str__(self):
        return f"{self.user.username} rated {self.book.title}: {self.rating}"


class BookComment(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    commented_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        truncated_comment = self.comment[:50]
        if len(self.comment) > 50:
            truncated_comment += "..."
        return f"{self.user.username} commented on {self.book.title}: {truncated_comment}"


class Featured(models.Model):
    book = models.ForeignKey(
        Book, on_delete=models.SET_NULL, blank=True, null=True)
