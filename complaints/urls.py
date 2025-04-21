from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_complaint, name='submit_complaint'),
    path('list/', views.complaint_list, name='complaint_list'),
    path('my-complaints/', views.my_complaints, name='my_complaints'),
    path('track/', views.track_complaint_status, name='track_complaint'), # Page with form
    # URLs using complaint's primary key (UUID) for internal linking
    path('<uuid:pk>/detail/', views.complaint_detail, name='complaint_detail'),
    path('<uuid:pk>/receipt/', views.complaint_receipt, name='complaint_receipt'),
    path('<uuid:pk>/edit/', views.edit_complaint, name='edit_complaint'),
    path('<uuid:pk>/delete/', views.delete_complaint, name='delete_complaint'),
    path('<uuid:pk>/respond/', views.respond_complaint, name='respond_complaint'),
    # No separate URL needed for mark_viewed, it happens in detail view
]