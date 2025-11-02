from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.home, name='home'),
    path('registration/', views.registration, name='signup'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('all_books/', views.all_books, name='all_books'),
    path('book/<int:id>/', views.book, name='book'),
    path('book/<int:book_id>/comment/<int:comment_id>/delete/',
         views.delete_comment, name='delete_comment'),
    path('all_writers/', views.all_writers, name='all_writers'),
    path('writer/<int:id>/', views.writer, name='writer'),
    path('add_wishlist/<int:id>/', views.add_wishlist, name='add_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('delete_wishlist/<int:id>/',
         views.delete_wishlist, name='delete_wishlist'),
    path('discover/', views.discover, name='discover'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
