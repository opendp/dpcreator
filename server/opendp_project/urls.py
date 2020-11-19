"""opendp_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from rest_framework import routers, serializers

from opendp_apps.dataset.views import DepositorSetup
from opendp_apps.user.models import OpenDPUser
from opendp_apps.user.views import UserViewSet  #, SessionViewSet
from opendp_apps.user.views import GoogleLogin
from opendp_project import settings
from opendp_apps.content_pages.views import view_opendp_welcome

admin.site.site_header = 'OpenDP App Admin Panel'
admin.site.site_title = 'OpenDP App Admin Panel'


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OpenDPUser
        fields = ['url', 'username', 'email', 'is_staff']


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
#router.register(r'sessions', SessionViewSet)


urlpatterns = [
    url(r'^$', view_opendp_welcome, name='welcome_page'),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
    path('api/deposit/', DepositorSetup.as_view()),

    url('r^home/$', TemplateView.as_view(template_name="home.html"), name='home'),
    url(r'^signup/$', TemplateView.as_view(template_name="signup.html"),
      name='signup'),
    url(r'^email-verification/$',
      TemplateView.as_view(template_name="email_verification.html"),
      name='email-verification'),
    url(r'^login/$', TemplateView.as_view(template_name="login.html"),
      name='login'),
    url(r'^logout/$', TemplateView.as_view(template_name="logout.html"),
      name='logout'),
    url(r'^password-reset/$',
      TemplateView.as_view(template_name="password_reset.html"),
      name='password-reset'),
    url(r'^password-reset/confirm/$',
      TemplateView.as_view(template_name="password_reset_confirm.html"),
      name='password-reset-confirm'),

    url(r'^user-details/$',
      TemplateView.as_view(template_name="user_details.html"),
      name='user-details'),
    url(r'^password-change/$',
      TemplateView.as_view(template_name="password_change.html"),
      name='password-change'),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^account/', include('allauth.urls')),
    url(r'^accounts/profile/$', RedirectView.as_view(url='/', permanent=True), name='profile-redirect'),
    url(r'^rest-auth/google/$', GoogleLogin.as_view(), name='google-login'),

                  # Putting all vue-related views under "ui/" for now to separate from the api.
    path('ui/', TemplateView.as_view(template_name='index.html'), name='index'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, kwargs={'show_indexes': True})
