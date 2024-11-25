from rest_framework import generics
from .models import Profile
from .serializers import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound

class CreateProfileView(generics.CreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)

            profile = user.profile 
            profile_serializer = ProfileSerializer(profile)

            return Response({
                'token': token.key,
                'profile': profile_serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'message': 'User is not logged in.'}, status=status.HTTP_400_BAD_REQUEST)
        
class EditProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        profile = user.profile  

        # First, validate and save the user data
        user_serializer = UserSerializer(user, data=request.data.get('user', {}), partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Now validate and save the profile data
        profile_data = request.data.copy()
        profile_data['user'] = user_serializer.data  # Ensure the user data is included

        profile_serializer = ProfileSerializer(profile, data=profile_data, partial=True)
        if profile_serializer.is_valid():
            profile_serializer.save()

            # If tutor data is included and needs to be updated, we handle that separately
            tutor_data = request.data.get('tutor', None)
            if tutor_data:
                tutor_serializer = TutorSerializer(profile.tutor, data=tutor_data, partial=True)
                if tutor_serializer.is_valid():
                    tutor_serializer.save()
                else:
                    return Response(tutor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'profile': profile_serializer.data
        }, status=status.HTTP_200_OK)
    
class GetProfileByIdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile_id = request.query_params.get('profile_id') 
        if not profile_id:
            profile = request.user.profile
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)

        try:
            profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            raise NotFound(detail="Profile not found.")

        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
