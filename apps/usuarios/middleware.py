from django.contrib.sessions.models import Session
from django.contrib.auth import logout
from django.utils import timezone


class LimitUserSessionsMiddleware:
    """Middleware para limitar sessões por usuário"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Limitar a 3 sessões ativas por usuário
            current_session_key = request.session.session_key
            
            # Buscar todas as sessões do usuário
            user_sessions = Session.objects.filter(
                expire_date__gte=timezone.now()
            )
            
            user_session_keys = []
            for session in user_sessions:
                data = session.get_decoded()
                if data.get('_auth_user_id') == str(request.user.id):
                    user_session_keys.append(session.session_key)
            
            # Se tiver mais de 3 sessões, deletar as mais antigas
            if len(user_session_keys) > 3:
                sessions_to_delete = user_session_keys[:-3]
                Session.objects.filter(session_key__in=sessions_to_delete).delete()
        
        response = self.get_response(request)
        return response
