
from rest_framework import serializers
from .models import User, Profile, Company , Application , Job, Job_category , Skill 
  
class ApplicationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Application
    fields = '__all__'
    
  def __init__(self, *args, **kwargs):
        super(ApplicationSerializer, self).__init__(*args, **kwargs)
        if 'instance' in self.context:
          for field_name in ['user', 'job']:
            self.fields[field_name].required = False
    
class SkillSerializer(serializers.ModelSerializer):
  class Meta:
    model = Skill
    fields = '__all__'
  
class JobSerializer(serializers.ModelSerializer):
    applications = ApplicationSerializer(many=True)
    skills = SkillSerializer(many=True, read_only=True)
    
    class Meta:
      model = Job
      fields = '__all__'
      extra_kwargs = {
        'user': {'required': False}
      }
    

    def to_representation(self, instance):
        # Customize the representation for 'skills' to be an array
        representation = super(JobSerializer, self).to_representation(instance)
        representation['skills'] = SkillSerializer(instance.skills.all(), many=True).data
        return representation



class ProfileSerializer(serializers.ModelSerializer):
  skills = SkillSerializer(many=True, read_only=True)
  user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
  class Meta:
    model = Profile
    fields = '__all__'
  
    
class UserSerializer(serializers.ModelSerializer):
  # jobs = JobSerializer(many=True)
  # profile = ProfileSerializer()
  # applications = ApplicationSerializer(many=True)
  class Meta:
    model = User
    fields = ('pk','username', 'first_name', 'last_name')

class CompanySerializer(serializers.ModelSerializer):
      # user = UserSerializer(required = True)
    class Meta:
        model = Company
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super(CompanySerializer, self).__init__(*args, **kwargs)
        if 'instance' in self.context:
          for field_name in ['user']:
            self.fields[field_name].required = False
      


class Job_categorySerializer(serializers.ModelSerializer):
  jobs = JobSerializer(many=True, read_only=True)
  class Meta:
      model = Job_category
      fields = '__all__'

