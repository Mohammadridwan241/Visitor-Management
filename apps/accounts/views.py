from django.contrib.auth.views import LoginView, LogoutView
from rest_framework import serializers
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class ReceptionLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class ReceptionLogoutView(LogoutView):
    pass


class LogoutSerializer(serializers.Serializer):
    pass


class ApiLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        request.session.flush()
        return Response({'detail': 'Logged out.'}, status=status.HTTP_200_OK)
