from users.models import User
from client.models import Client


class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Attach staff user
        staff_id = request.session.get('staff_id')
        if staff_id:
            try:
                request.current_user = User.objects.get(pk=staff_id, statut=True)
            except User.DoesNotExist:
                request.current_user = None
                del request.session['staff_id']
        else:
            request.current_user = None

        # Attach client
        client_id = request.session.get('client_id')
        if client_id:
            try:
                request.current_client = Client.objects.get(pk=client_id)
            except Client.DoesNotExist:
                request.current_client = None
                del request.session['client_id']
        else:
            request.current_client = None

        response = self.get_response(request)
        return response
