"""
URL configuration for djangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from views import show_top_nbu_rates, show_image, url_validate, metadata_text, info
from views import entity_list, entity_detail, create_entity, delete_entity

urlpatterns = [
    path("nbu_rates/", show_top_nbu_rates, name="rates"),
    path("image/<str:imagepth>", show_image, name="image"),
    path("url_validate/", url_validate, name="url_validate"),
    path("metadata/", metadata_text, name="metadata_text"),
    path('entity/', entity_list, name='entity_list'),
    path('entity/<int:id>/', entity_detail, name='entity_detail'),
    path('entity/create/', create_entity, name='create_entity'),
    path('entity/<int:id>/delete/', delete_entity, name='delete_entity'),
    path("info/", info, name="info")
]
