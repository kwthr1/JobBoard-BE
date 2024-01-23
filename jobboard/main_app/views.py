from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from .serializers import Job_categorySerializer, JobSerializer, CompanySerializer, SkillSerializer, ProfileSerializer, ApplicationSerializer, UserSerializer

from .models import Skill, Profile, Company, Job_category, Job, Application, User
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated, AllowAny, AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes
from rest_framework import permissions
from rest_framework import status
from rest_framework import generics
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist 

from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.decorators import permission_required
from .decorator import allowed_users
# Create your views here.
from django.utils.decorators import method_decorator

@api_view(['GET'])
def hello_world(request):
    return Response({'message': 'Hello, world!'})

# Job-Category views:

class JobCategoryList(generics.ListAPIView):
    queryset = Job_category.objects.all()
    serializer_class = Job_categorySerializer

    # def get(self, request, *args, **kwargs):
    #     job_categories = Job_categorySerializer(self.get_queryset(), many=True).data
    #     return Response(job_categories)
 

class JobCategoryDetail(DetailView):
    model = Job_category

    def get(self, request, *args, **kwargs):
        job_category = Job_categorySerializer(self.get_queryset()).data
        return Response(job_category)


# @allowed_users(['A'])
@method_decorator(allowed_users([]), name='dispatch')
class JobCategoryCreate(generics.CreateAPIView):
    # model = Job_category
    serializer_class = Job_categorySerializer
    permission_class = [IsAuthenticated]
    
    # fields = ['category_name']
    def form_valid(self, form):
        instance = form.save(commit=False)
        job_category = self.serializer_class(instance)
        return Response(job_category)



class JobCategoryUpdate(UpdateView):
    # model = Job_category
    # fields = ['category_name']

    serializer_class = Job_categorySerializer
    permission_class = [IsAuthenticated]
    
    # fields = ['category_name']
    def form_valid(self, form):
        instance = form.save(commit=False)
        job_category = self.serializer_class(instance)
        return Response(job_category)



class JobCategoryDelete(DeleteView):
    model = Job_category
    permission_class = [AllowAny]

    # success_url = '/job_categories'
    def delete(self, request, *args, **kwargs):
        # self.check_object_permissions(self.request, self.get_object())
        response = super().delete(request, *args, **kwargs)
        return Response({'message': 'Job deleted successfully'})


# Job Views:

class JobList(generics.ListAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    # def get(self, request, *args, **kwargs):
    #     job_list = JobSerializer(self.get_queryset(), many=True).data
    #     return Response(job_list)


class JobDetail(DetailView):
    model = Job

    def get(self, request, *args, **kwargs):
        job= JobSerializer(self.get_queryset()).data
        return Response(job)

# class JobCreate(generics.CreateAPIView):
#     queryset = Job.objects.all()
#     serializer_class = JobSerializer

#     def perform_create(self, serializer):
#         # Exclude 'user' from validated_data during creation
#         user = self.request.user if self.request.user.is_authenticated else None
#         serializer.save(user=user)


@parser_classes([JSONParser])
class JobCreate(generics.CreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = self.request.user if self.request.user.is_authenticated else None

        # Convert skills to list if provided as a comma-separated string
        if 'skills' in request.data and isinstance(request.data['skills'], str):
            request.data['skills'] = [skill.strip() for skill in request.data['skills'].split(',')]

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
# class JobCreate(generics.CreateAPIView):
#     # model = Job_category
#     serializer_class = JobSerializer
#     permission_class = [IsAuthenticated]
    
#     # fields = ['category_name']
#     def form_valid(self, form):
#         instance = form.save(commit=False)
#         job = self.serializer_class(instance)
#         return Response(job)
    
# class JobCreate(LoginRequiredMixin, CreateView):
#     serializer_class = JobSerializer
    
#     # fields = ['job_title', 'job_description', 'job_salary']

#     def form_valid(self, form):
#         instance = form.save(commit=False)
#         job = self.serializer_class(instance)
#         return Response(job)


class JobUpdate(UpdateView):
    model = Job
    fields = ['job_title', 'job_description', 'job_salary']


class JobDelete(DeleteView):
    model = Job
    success_url = '/jobs'

# @api_view(['GET'])
# def application_index(request):
# #   applications = Application.objects.filter(user=request.user)
# # just 4 tesing 
#   applications = Application.objects.all()  
#   return Response({'applications' : applications})

@allowed_users(['J'])
@csrf_exempt
@api_view(['GET'])
def application_list(request):
    applications = Application.objects.filter(user_id=request.user.id)
    # serialized_applications = [ApplicationSerializer(instance=app).data for app in applications]
    application_serializer = ApplicationSerializer(applications, many=True)
    # return JsonResponse(application_serializer.data , safe=False)
    serialized_data = application_serializer.data
    return JsonResponse({'applications': serialized_data})

@csrf_exempt
@api_view(['GET'])
def get_user_info(request,user_id):
    user_info = User.objects.get(id=user_id)
    user_serializer = UserSerializer(user_info)
    profile_info = Profile.objects.get(user = user_info)
    # profile_info = get_object_or_404(Profile, user=user_info)
    profile_serializer = ProfileSerializer(profile_info)
    response_data = {
        "user_info": user_serializer.data,
        "profile_info": profile_serializer.data
    }
    return JsonResponse(response_data)

@csrf_exempt
@permission_classes([permissions.IsAuthenticated])
@api_view(['POST'])
def application_create(request , user_id , job_id):
    user_id = request.user.id
    print("user_id",request.user.id)
    if 'resume' in request.FILES:
        resume_file = request.FILES['resume']
    if not resume_file.name.endswith('.pdf'):
        return JsonResponse({"error": "Only PDF format is accepted"})   
    
    application_data = {
            'user': user_id,
            'job': job_id,
            'resume': resume_file
        }
    
    application_serializer = ApplicationSerializer(data=application_data)
    if application_serializer.is_valid():
            # Save the application to the database
            application_serializer.save()

            # Retrieve the serialized data of the created application
            serialized_application = ApplicationSerializer(application_serializer.instance).data

            return JsonResponse({
                "message": "Application created successfully",
                "application": serialized_application
            })
    else:
            return JsonResponse({"error": application_serializer.errors})
  
@csrf_exempt
@permission_classes([permissions.IsAuthenticated])
@api_view(['POST'])
def application_update(request):
    application_id = request.GET.get('application_id')
    application_info = Application.objects.get(id=application_id)
    # making sure that the user who created the application is the one who's updating the application
    if  request.user.id != application_info.user_id:
        JsonResponse({"error" : "You are not authorized to update this application"})
    if 'resume' in request.FILES:
        resume_file = request.FILES['resume']
    if not resume_file.name.endswith('.pdf'):
        return JsonResponse({"error": "Only PDF format is accepted"})  
        
    print("Before assigning user:", application_info.user)
    print("Before assigning job:", application_info.job)
    application_info.resume = resume_file
    application_info.user = request.user
    print('user id in update application' , request.user)
    application_info.job= application_info.job
    print('job id in update application' ,  application_info.job)

    
    application_serializer = ApplicationSerializer(instance=application_info, data=request.data , context={'instance':application_info})
    if application_serializer.is_valid():
        application_serializer.save()

        # Retrieve the serialized data of the updated application
        serialized_application = ApplicationSerializer(application_info).data

        return JsonResponse({
            "message": "Application updated successfully",
            "application": serialized_application
        })
    else:
        return JsonResponse({"error": application_serializer.errors})

@csrf_exempt
@api_view(['GET'])  
def application_delete(request):
    application_id = request.GET.get('application_id')
    print('application_id =' , application_id )
    try:
        application_info = Application.objects.get(id=application_id)
        print('applicatoin_info' , application_info)
        application_info.delete()
        response_data = {'success': True, 'message': ' Your application deleted successfully'}
    except ObjectDoesNotExist as e:
        print(f'Application.DoesNotExist: {str(e)}')
        response_data = {'success': False, 'message': 'Application not found'}
    return JsonResponse(response_data)

@csrf_exempt
@permission_classes([permissions.IsAuthenticated])  
@api_view(['POST'])  
def assoc_job(request):
    job_id = request.GET.get('job_id')
    print('job_id', job_id)
    skill_id=request.GET.get('skill_id')
    print('skill_id', skill_id)
    try:
        job = Job.objects.get(id=job_id)
        skill = Skill.objects.get(id=skill_id)
        print('skill', skill )

            # Add the skill to the job's skills
        job.skills.add(skill)
        print('job', job)
        print('added job to skill' , job.skills.add(skill))
        job_serializer = JobSerializer(job)
        return JsonResponse({
            'message': "The skill has been added successfully from the job",
            'job': job_serializer.data
        })    
    except Job.DoesNotExist:
        return JsonResponse({'message': 'Job not found'})

    except Skill.DoesNotExist:
        return JsonResponse({'message': 'Skill not found'})

    except Exception as e:
        return JsonResponse({'message': str(e)})
    
@csrf_exempt
@permission_classes([permissions.IsAuthenticated])  
@api_view(['POST'])  
def unassoc_job(request):
    job_id = request.GET.get('job_id')
    print('job_id', job_id)
    skill_id=request.GET.get('skill_id')
    print('skill_id', skill_id)
    try:
        job = Job.objects.get(id=job_id)
        skill = Skill.objects.get(id=skill_id)
        print('skill', skill )

            # Add the skill to the job's skills
        job.skills.remove(skill)
        print('job', job)
        job_serializer = JobSerializer(job)
        return JsonResponse({
            'message': "The skill has been removed successfully from the job ",
            'job': job_serializer.data
        })  
    except Job.DoesNotExist:
        return JsonResponse({'message': 'Job not found'})

    except Skill.DoesNotExist:
        return JsonResponse({'message': 'Skill not found'})

    except Exception as e:
        return JsonResponse({'message': str(e)})


@csrf_exempt
@api_view(['POST'])    
@permission_classes([permissions.IsAuthenticated])  
def assoc_profile(request):
    user_id = request.user.id
    print('user_id', user_id)
    skill_id = request.GET.get('skill_id')
    print('skill_id', skill_id)
    try:
        profile = Profile.objects.get(user_id=user_id)
        print('profile_info', profile)
        # skill = Skill.objects.get(id=skill_id)
        profile.skills.add(skill_id)
        profile_serializer = ProfileSerializer(profile)
        return JsonResponse({
            'message': "The skill has been removed successfully from the User Profile",
            'profile': profile_serializer.data
        })      
    except Profile.DoesNotExist:
        return JsonResponse({'message' : "profile does not exist"})
    except Skill.DoesNotExist:
        return JsonResponse({'message' : "skill does not exist"})
    except Exception as e:
        return JsonResponse({'message': str(e)})

@csrf_exempt
@permission_classes([permissions.IsAuthenticated])  
@api_view(['POST']) 
def unassoc_profile(request):
    user_id = request.user.id
    print('user_id', user_id)
    skill_id = request.GET.get('skill_id')
    print('skill_id', skill_id)
    try:
        profile = Profile.objects.get(user_id=user_id)
        print('profile_info', profile)
        # skill = Skill.objects.get(id=skill_id)
        profile.skills.remove(skill_id)
        profile_serializer = ProfileSerializer(profile)
        return JsonResponse({
            'message': "The skill has been removed successfully from the User Profile",
            'profile': profile_serializer.data
        }) 
    except Profile.DoesNotExist:
        return JsonResponse({'message' : "profile does not exist"})
    except Skill.DoesNotExist:
        return JsonResponse({'message' : "skill does not exist"})
    except Exception as e:
        return JsonResponse({'message': str(e)})
        
# def application_delete(request):
#     application_id = request.GET.get('application_id')
#     try:
#         application_info = Application.objects.get(id=application_id)
#         application_info.delete()
#         response_data = {'success': True, 'message': 'Application deleted successfully'}
#     except ObjectDoesNotExist:
#         response_data = {'success': False, 'message': 'Application not found'}
#     return JsonResponse(response_data)



    # ApplicationForm(request.POST, request.FILES) 
    # if form.is_valid():
    #     new_application = form.save(commit=False) 
    #     # get the job and user id from the url and add it as fk
    #     # add fk manually
    #     new_application.user_id = user_id
    #     new_application.job_id = job_id
    #     uploaded_file = request.FILES.get('resume')
    #     if uploaded_file:
    #         new_application.resume = uploaded_file
        
    #     new_application.save()
    #     serialized_application = ApplicationForm(instance=new_application).data
    #     # return JsonResponse()
    #     # return Response({'success': True, 'application': serialized_application})
    # else:
    #     return Response({'success': False, 'errors': form.errors})


class CompanyList(generics.ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    # def get(self, request, *args, **kwargs):
    #     company_list = CompanySerializer(self.get_queryset(), many=True).data
    #     return Response(company_list)

# class CompanyDetail(DetailView):
#     model = Company

#     def get(self, request, *args, **kwargs):
#         company = CompanySerializer(self.get_queryset()).data
#         return Response(company)
    
class CompanyDetail(generics.RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

# class CompanyCreate(generics.CreateAPIView):
#     serializer_class = CompanySerializer
#     # permission_class = [IsAuthenticated]
#     queryset = Company.objects.all()
#     parser_classes = (MultiPartParser, FormParser)
@csrf_exempt
@permission_classes([permissions.IsAuthenticated])
@api_view(['POST'])
def company_create(request):
    try:
        user_id = request.user.id
        company_name = request.data['company_name']
        location = request.data['location']
        logo = request.FILES['logo']
        email = request.data['email']
        
        company = Company.objects.create(
            user_id=user_id,
            company_name=company_name,
            location=location,
            logo=logo,
            email=email
        )    
        serialized_company_data = CompanySerializer(company)
        return JsonResponse(serialized_company_data.data)
    except  Exception as e:
        return JsonResponse({'message': str(e)})
    
@csrf_exempt
@permission_classes([permissions.IsAuthenticated])
@api_view(['POST'])
def company_update(request):
        company_id = request.GET.get('company_id')
        company_info = Company.objects.get(id = company_id)
        
        company_info.company_name = request.data.get('company_name')
        company_info.location = request.data.get('location')
        company_info.logo = request.FILES.get('logo')
        company_info.email = request.data.get('email')
        
        serialized_data = CompanySerializer(instance=company_info , data=request.data, context={'instance':company_info})
        
        if serialized_data.is_valid():
            serialized_data.save()
        
            updated_serialized_company = CompanySerializer(company_info).data
            
            return JsonResponse({
                "message": "Company updated successfully",
                "company": updated_serialized_company
            })
        else:
            return JsonResponse({"error": updated_serialized_company.errors})
   
        
        
     
    # fields = ['company_name', 'location', 'logo', 'email']

    # def form_valid(self, form):
    #     instance = form.save(commit=False)
    #     job = self.serializer_class(instance)
    #     return Response(job)
    
    # def form_valid(self, form):
    #   form.instance.user = self.request.user
    #   # super() is calling the parent class
    #   return super().form_valid(form)

class CompanyUpdate(generics.UpdateAPIView):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    # model = Company
    # fields = ['company_name', 'location', 'logo', 'email']

class CompanyDelete(generics.DestroyAPIView):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()

class ProfileList(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class ProfileCreate(generics.CreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class ProfileUpdate(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class ProfileDelete(generics.DestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    
# @csrf_exempt
# def signup(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return Response({'success': True, 'message': 'Signup successful'})
#         else:
#             return Response({'success': False, 'message': 'Invalid sign up - try again'}, status=400)

#     return Response({'success': False, 'message': 'Bad request'}, status=400)


class RegistrationView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        role = request.data.get('role', 'J')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        phone_number = request.data.get('phone_number')
        image = request.data.get('image')


        if not username or not password or not email or not first_name or not last_name or not phone_number:
            return Response({'error': 'username, password, email, frist name, last name, and phone number are required'}, status=status.HTTP_400_BAD_REQUEST)
        if role not in ('J', 'C'):
            role = 'J'
        # Create user
        user = User.objects.create_user(username=username, password=password,)
        Profile.objects.create(email=email, user=user, role=role, first_name=first_name, last_name=last_name, phone_number=phone_number, image=image)

        login(request, user)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({'access_token': access_token, 'refresh_token': str(refresh) }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Both username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Login the user
            login(request, user)

            # Generate new tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({'access_token': access_token, 'refresh_token': str(refresh)}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Log out the user
        logout(request)

        return Response({'detail': 'Successfully logged out'}, status=status.HTTP_200_OK)

class SkillList(generics.ListAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

    # def get(self, request, *args, **kwargs):
    #     skills = SkillSerializer(self.get_queryset(), many=True).data
    #     return Response(skills)

class SkillDetail(DetailView):
    model = Skill

class SkillCreate(generics.CreateAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    # model = Skill
    # fields = ['skill_name']
    

class SkillUpdate(generics.UpdateAPIView):
    # model = Skill
    # fields = ['skill_name']
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

class SkillDelete(generics.DestroyAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    

@csrf_exempt
@api_view(['GET'])
def get_jobs_by_category(request):
    category_id = request.GET.get('category_id')
    print('category_id' , category_id)
    try:
        jobs = Job.objects.filter(job_category_id = category_id)
        job_serializer = JobSerializer(jobs, many=True)
        return JsonResponse(job_serializer.data, safe=False)
    except Exception as e:
        return JsonResponse({'message': str(e)})
    
@csrf_exempt
@api_view(['GET'])
def get_user_role(request):
    user_id = request.user.id
    print("user_id", user_id)
    try:
        user_role = Profile.objects.filter(user_id = user_id).values_list('role')[0]
        # user_role = Profile.objects.filter
        # user_role = Profile.objects.values_list('role', flat=True)[0]
        print('user_role ' , user_role)
        # profile_serializer = ProfileSerializer(user_role)
        return JsonResponse(user_role[0], safe=False)
    except Exception as e:
        return JsonResponse({'message': str(e)})

@csrf_exempt
@api_view(['GET'])
def get_jobs_by_company(request):
    company_id = request.GET.get('id')
    try:
        company_jobs = Job.objects.filter(company_id = company_id)
        company_job_serializer = JobSerializer(company_jobs , many=True)
        job_company_response = {
            'jobs': company_job_serializer.data
        }
        return JsonResponse(job_company_response)
    except Exception as e:
        return JsonResponse({'message': str(e)})