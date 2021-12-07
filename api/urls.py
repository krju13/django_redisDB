from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import manage_items,manage_item, manage_json,manage_json_detail, manage_hash_person,manage_hash_person_detail

urlpatterns={
    path('itme/',manage_items, name="itmes"),
    path('itme/<slug:key>/',manage_item,name="single_item"),
    path('json/',manage_json,name="json"),
    path('json/<int:pk>/',manage_json_detail,name="json_detail"),
    path('hash/',manage_hash_person.as_view(),name="hashtest"),
    path('hash/<int:pk>/',manage_hash_person_detail.as_view(),name="hashtest"),
}
urlpatterns=format_suffix_patterns(urlpatterns)
