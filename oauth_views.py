from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.yandex.views import YandexOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialApp
from django.urls import reverse

def google_login_direct(request):
    """Redirect directly to Google OAuth"""
    try:
        app = SocialApp.objects.get(provider='google')
        adapter = GoogleOAuth2Adapter(request)
        client = OAuth2Client(
            request,
            app.client_id,
            app.secret,
            adapter.access_token_method,
            adapter.access_token_url,
            adapter.callback_url,
            adapter.scope,
            adapter.redirect_uri_param_name,
            adapter.headers,
            adapter.basic_auth,
            adapter.requests_session,
        )
        
        # Get the authorization URL
        auth_url = client.get_redirect_url(adapter.authorize_url, {
            'client_id': app.client_id,
            'redirect_uri': adapter.callback_url,
            'scope': ' '.join(adapter.scope),
            'response_type': 'code',
            'state': adapter.get_state_param(),
        })
        
        return redirect(auth_url)
    except Exception as e:
        # Fallback to regular allauth flow
        return redirect('/accounts/google/login/')

def yandex_login_direct(request):
    """Redirect directly to Yandex OAuth"""
    try:
        app = SocialApp.objects.get(provider='yandex')
        adapter = YandexOAuth2Adapter(request)
        client = OAuth2Client(
            request,
            app.client_id,
            app.secret,
            adapter.access_token_method,
            adapter.access_token_url,
            adapter.callback_url,
            adapter.scope,
            adapter.redirect_uri_param_name,
            adapter.headers,
            adapter.basic_auth,
            adapter.requests_session,
        )
        
        # Get the authorization URL
        auth_url = client.get_redirect_url(adapter.authorize_url, {
            'client_id': app.client_id,
            'redirect_uri': adapter.callback_url,
            'scope': ' '.join(adapter.scope),
            'response_type': 'code',
            'state': adapter.get_state_param(),
        })
        
        return redirect(auth_url)
    except Exception as e:
        # Fallback to regular allauth flow
        return redirect('/accounts/yandex/login/')
