from rest_framework.views import APIView
from rest_framework import status, permissions
from .serializers import (
    RegisterUserSerializer,
    LoginUserSerializer,
    LogoutUserSerializer,
    )
from rest_framework.response import Response





class UserRegisterViewAPI(APIView):
    """
    API endpoint that allows users Register.
    """
    serializer_class = RegisterUserSerializer

    def post(self, request):
        srz_data = self.serializer_class(
            data=request.data)
        if srz_data.is_valid():
            srz_data.save()
            return Response(
                data={
                    'data': srz_data.data,
                    'message': 'your account has been created!'
                    },
                    status=status.HTTP_201_CREATED
                    )
        return Response(data=srz_data.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUserAPI(APIView):
    """
    API endpoint that allows users Login.
    """
    def post(self, request):
        srz_data = LoginUserSerializer(data=request.data)
        if srz_data.is_valid():
            tokens = srz_data.validated_data['tokens']
            user_info = srz_data.validated_data['user-info']
            return Response(data={'tokens': tokens, 'user-info': user_info}, status=status.HTTP_200_OK)
        return Response(data=srz_data.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutUserAPI(APIView):
    """
    API endpoint that allows users Logout.
    """
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request):
        srz_data = LogoutUserSerializer(data=request.data)
        if srz_data.is_valid():
            return Response(
                data={'message': 'you logged out successfully!!'},
                status=status.HTTP_200_OK
                )
        return Response(data=srz_data.errors, status=status.HTTP_400_BAD_REQUEST)