import os
from rest_framework import generics
from .models import Profile
from .serializers import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound
from django.core.files.base import ContentFile
from PIL import Image
import io

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
            token, _ = Token.objects.get_or_create(user=user)

            profile = user.profile 
            profile_serializer = ProfileSerializer(profile)

            return Response({
                'token': token.key,
                'profile': profile_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class EditProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        user = request.user
        profile = user.profile  

        if not self.update_user(user, request.data):
            return Response({'detail': 'Error updating user.'}, status=status.HTTP_400_BAD_REQUEST)

        profile_picture = request.data.get('profile_picture')
        
        if profile_picture:
            if not self.handle_profile_picture(profile, profile_picture):
                return Response({'detail': 'Error processing profile picture.'}, status=status.HTTP_400_BAD_REQUEST)

        if not self.update_is_tutor(profile, request.data):
            return Response({'detail': 'Error updating profile.'}, status=status.HTTP_400_BAD_REQUEST)

        if not self.update_tutor(profile, request.data):
            return Response({'detail': 'Error updating tutor information.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'profile': ProfileSerializer(profile).data}, status=status.HTTP_200_OK)

    def update_user(self, user, data):
        user_data = {
            'first_name': data.get('user[first_name]'),
            'last_name': data.get('user[last_name]'),
            'email': data.get('user[email]')
        }
        user_serializer = UserSerializer(user, data=user_data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return True
        return False

    def handle_profile_picture(self, profile, new_profile_picture):
        try:
            if profile.profile_picture:
                self.delete_existing_picture(profile.profile_picture.path)

            img = Image.open(new_profile_picture)
            img = img.resize((368, 368), Image.Resampling.LANCZOS)
            thumb_io = io.BytesIO()
            img.save(thumb_io, format='JPEG')
            thumb_file = ContentFile(thumb_io.getvalue(), name=new_profile_picture.name)
            profile.profile_picture.save(thumb_file.name, thumb_file)
            return True
        except Exception as e:
            return False

    def delete_existing_picture(self, path):
        if os.path.isfile(path):
            os.remove(path)

    def update_is_tutor(self, profile, data):
        profile_data = {
            'is_tutor': data.get('is_tutor'),
        }
        profile_serializer = ProfileSerializer(profile, data=profile_data, partial=True)
        if profile_serializer.is_valid():
            profile_serializer.save()
            return True
        return False

    def update_tutor(self, profile, data):
        if not profile.is_tutor:
            return True  

        tutor_data = {
            'id': data.get('tutor[id]'),
            'about': data.get('tutor[about]', None),
            'birth_date': data.get('tutor[birth_date]') or None,
            'education': data.get('tutor[education]', None),
            'links': data.get('tutor[links]', None),
            'experienceYears': data.get('tutor[experienceYears]', None),
            'paymentMethod': data.get('tutor[paymentMethod]', None),
            'totalRating': profile.tutor.totalRating,
            'peopleReacted': profile.tutor.peopleReacted,
        }

        for key in tutor_data:
            if tutor_data[key] == 'null':
                tutor_data[key] = None
                
        tutor_serializer = TutorSerializer(profile.tutor, data=tutor_data, partial=True)
        if tutor_serializer.is_valid():
            tutor_serializer.save()
            return True
        return False


    
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

class GetUsersByFullNameView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        full_name = request.query_params.get('full_name')
        if not full_name:
            return Response({'detail': 'Full name parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        name_parts = full_name.split(' ')
        if len(name_parts) != 2:
            return Response({'detail': 'Please provide both first and last name.'}, status=status.HTTP_400_BAD_REQUEST)

        first_name, last_name = map(str.capitalize, name_parts)

        users = User.objects.filter(first_name__icontains=first_name, last_name__icontains=last_name)

        if not users.exists():
            users = User.objects.filter(first_name__icontains=last_name, last_name__icontains=first_name)

        if not users.exists():
            raise NotFound(detail="No users found with that name.")

        user_data = [{"id": user.id, "first_name": user.first_name, "last_name": user.last_name} for user in users]

        return Response(user_data, status=status.HTTP_200_OK)