from rest_framework import serializers
from .models import Company, Employee,MainTraining, SubTraining,EmployeeSubTraining,Project,Notification
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from datetime import timedelta, date
from rest_framework import generics

from .fields import CustomDateField

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class ProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name']

class EmployeeSerializer(serializers.ModelSerializer):
    company_id = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), source='company', write_only=True)
    project_id = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), source='project', write_only=True)
    company = CompanySerializer(read_only=True)
    project = ProjectsSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'fullname', 'mobile_number', 'designation', 'gate_pass_no',
            'rig_or_rigless', 'company_id', 'project_id', 'profile_photo', 'is_accepted','company','project','on_duty'
        ]
    
    def get_profile_photo(self, obj):
        request = self.context.get('request')
        if obj.profile_photo:
            return request.build_absolute_uri(obj.profile_photo.url)
        return None

class EmployeePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['profile_photo']
    

class SubTrainingSerializer(serializers.ModelSerializer):
    main_training = serializers.PrimaryKeyRelatedField(queryset=MainTraining.objects.all())

    VALIDITY_CHOICES = {
        '6 months': timedelta(days=182),
        '1 year': timedelta(days=365),
        '2 years': timedelta(days=365 * 2),
        '3 years': timedelta(days=365 * 3),
        '4 years': timedelta(days=365 * 4),
        '5 years': timedelta(days=365 * 5),
        'Permanent': None,
    }

    validity_period = serializers.ChoiceField(choices=list(VALIDITY_CHOICES.keys()))

    class Meta:
        model = SubTraining
        fields = ['id','main_training', 'name', 'validity_period']

    def create(self, validated_data):
        validity_period_str = validated_data.pop('validity_period')
        validity_period = self.VALIDITY_CHOICES[validity_period_str]
        sub_training = SubTraining.objects.create(validity_period=validity_period, **validated_data)
        return sub_training

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        validity_period = instance.validity_period
        if validity_period is None:
            representation['validity_period'] = 'Permanent'
        else:
            for period_str, period_timedelta in self.VALIDITY_CHOICES.items():
                if period_timedelta == validity_period:
                    representation['validity_period'] = period_str
                    break
        return representation
    
class SubTrainingUpdateSerializer(serializers.ModelSerializer):
    subtraining_id = serializers.IntegerField(source='id')
    main_training = serializers.PrimaryKeyRelatedField(queryset=MainTraining.objects.all())
    validity_period = serializers.SerializerMethodField()

    class Meta:
        model = SubTraining
        fields = ['main_training', 'subtraining_id', 'name', 'validity_period']

    def get_validity_period(self, obj):
        if obj.validity_period:
            years = obj.validity_period.days // 365
            if years > 1:
                return f"{years} years"
            elif years == 1:
                return "1 year"
            months = (obj.validity_period.days % 365) // 30
            if months > 1:
                return f"{months} months"
            elif months == 1:
                return "1 month"
        return "No validity period"

class MainTrainingSerializer(serializers.ModelSerializer):
    # sub_trainings = SubTrainingSerializer(many=True, read_only=True)

    class Meta:
        model = MainTraining
        fields = '__all__'

class SubTrainingCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTraining
        fields = ['id', 'name', 'validity_period']

class MainTrainingCreateUpdateSerializer(serializers.ModelSerializer):
    sub_trainings = SubTrainingCreateUpdateSerializer(many=True, required=False)

    class Meta:
        model = MainTraining
        fields = ['id', 'name', 'sub_trainings']

    def update(self, instance, validated_data):
        # Update MainTraining fields
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        # Update SubTrainings if provided
        if 'sub_trainings' in validated_data:
            sub_trainings_data = validated_data.pop('sub_trainings')

            # Delete old sub trainings not in the update
            existing_ids = [sub.id for sub in instance.sub_trainings.all()]
            new_ids = [sub_data.get('id') for sub_data in sub_trainings_data if 'id' in sub_data]
            for id in existing_ids:
                if id not in new_ids:
                    SubTraining.objects.filter(id=id).delete()

            for sub_data in sub_trainings_data:
                if 'id' in sub_data:
                    sub_instance = SubTraining.objects.get(id=sub_data['id'], main_training=instance)
                    sub_instance.name = sub_data.get('name', sub_instance.name)
                    sub_instance.validity_period = sub_data.get('validity_period', sub_instance.validity_period)
                    sub_instance.save()
                else:
                    SubTraining.objects.create(main_training=instance, **sub_data)

        return instance

    

class CustomDateField(serializers.DateField):
    def __init__(self, *args, **kwargs):
        kwargs['input_formats'] = ['%d-%m-%Y']
        super().__init__(*args, **kwargs)

class EmployeeSubTrainingSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(required=False, format="%d-%m-%Y")
    expiration_date = serializers.DateField(required=False, format="%d-%m-%Y")
    completion_percentage = serializers.SerializerMethodField()
    pdf = serializers.FileField(required=False)
    sub_training_name = serializers.SerializerMethodField()
    main_training_name = serializers.SerializerMethodField()


    class Meta:
        model = EmployeeSubTraining
        fields = ['employee', 'sub_training', 'sub_training_name','main_training_name', 'start_date', 'expiration_date', 'warning', 'completion_percentage', 'pdf','verify_pdf']

    def validate(self, attrs):
        if 'start_date' not in attrs or attrs['start_date'] is None:
            attrs['start_date'] = None
        return attrs

    def create(self, validated_data):
        start_date = validated_data.get('start_date')
        sub_training = validated_data['sub_training']
        
        if start_date:
            if sub_training.validity_period:
                expiration_date = start_date + sub_training.validity_period
            else:
                expiration_date = None
            validated_data['expiration_date'] = expiration_date
        else:
            validated_data['start_date'] = None
            validated_data['expiration_date'] = None

        return super().create(validated_data)

    def get_completion_percentage(self, obj):
        if not obj.expiration_date or not obj.start_date:
            return 100.0
        if date.today() < obj.expiration_date:
            return 100.0
        return 0.0
    
    def get_sub_training_name(self, obj):
        return obj.sub_training.name
    
    def get_main_training_name(self, obj):
        return obj.sub_training.main_training.name


    
class AverageCompletionPercentageSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    average_completion_percentage = serializers.FloatField()

class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(label=("Email"), write_only=True)
    password = serializers.CharField(label=("Password"), style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError(("Invalid email or password."), code='authorization')

            user = authenticate(username=user.username, password=password)

            if user is None:
                raise serializers.ValidationError(("Invalid email or password."), code='authorization')
        else:
            raise serializers.ValidationError(("Must include 'email' and 'password'."), code='authorization')

        attrs['user'] = user
        return attrs

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class AcceptRejectEmployeeSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['accept', 'reject'])

    class Meta:
        fields = ['action']

class OnDutyOffDutyToggleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['on_duty']


class EmployeePercentageSubTrainingSerializer(serializers.ModelSerializer):
    completion_percentage = serializers.SerializerMethodField()
    sub_training_name = serializers.CharField(source='sub_training.name', read_only=True)
    main_training_name = serializers.CharField(source='sub_training.main_training.name', read_only=True)
    employee_name = serializers.CharField(source='employee.fullname', read_only=True)

    class Meta:
        model = EmployeeSubTraining
        fields = ['employee_name', 'sub_training_name', 'main_training_name', 'start_date', 'expiration_date', 'warning', 'completion_percentage']

    def get_completion_percentage(self, obj):
        return obj.calculate_completion()

class EmployeeMainTrainingSerializer(serializers.ModelSerializer):
    sub_training_name = serializers.CharField(source='sub_training.name', read_only=True)
    main_training_name = serializers.CharField(source='sub_training.main_training.name', read_only=True)
    employee_name = serializers.CharField(source='employee.fullname', read_only=True)
    completion_percentage = serializers.SerializerMethodField()
    start_percentage = serializers.SerializerMethodField()
    end_percentage = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    expiration_date = serializers.SerializerMethodField()
    sub_training_id = serializers.IntegerField(source='sub_training.id', read_only=True)
    employee_sub_training_id = serializers.IntegerField(source='id', read_only=True)
    pdf = serializers.FileField(required=False)
    verify_pdf = serializers.BooleanField(read_only=True)

    class Meta:
        model = EmployeeSubTraining
        fields = [
            'employee_name', 'main_training_name', 'sub_training_name',
            'start_date', 'expiration_date', 'warning',
            'completion_percentage', 'start_percentage', 'end_percentage',
            'pdf', 'sub_training_id', 'employee_sub_training_id','verify_pdf'
        ]

    def get_completion_percentage(self, obj):
        return obj.calculate_completion()

    def get_start_percentage(self, obj):
        return 100

    def get_end_percentage(self, obj):
        return 0

    def get_start_date(self, obj):
        return obj.start_date.strftime("%d/%m/%Y") if obj.start_date else None

    def get_expiration_date(self, obj):
        return obj.expiration_date.strftime("%d/%m/%Y") if obj.expiration_date else None

    
class MainTrainingsSerializer(serializers.ModelSerializer):
    sub_trainings = SubTrainingSerializer(many=True, read_only=True)

    class Meta:
        model = MainTraining
        fields = ['id', 'name', 'sub_trainings']



class SubTrainingWithMainNameSerializer(serializers.ModelSerializer):
    main_training_name = serializers.CharField(source='main_training.name', read_only=True)

    VALIDITY_CHOICES = {
        '6 months': timedelta(days=182),
        '1 year': timedelta(days=365),
        '2 years': timedelta(days=365 * 2),
        '3 years': timedelta(days=365 * 3),
        '4 years': timedelta(days=365 * 4),
        '5 years': timedelta(days=365 * 5),
        'Permanent': None,
    }

    class Meta:
        model = SubTraining
        fields = ['id', 'name', 'validity_period', 'main_training_name']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        validity_period = instance.validity_period
        validity_display = 'Unknown'

        if validity_period is None:
            validity_display = 'Permanent'
        else:
            for label, duration in self.VALIDITY_CHOICES.items():
                if duration == validity_period:
                    validity_display = label
                    break

        representation['validity_period'] = validity_display
        return representation

class MainTrainingWithSubSerializer(serializers.ModelSerializer):
    sub_trainings = serializers.SerializerMethodField()

    class Meta:
        model = MainTraining
        fields = ['id', 'name', 'sub_trainings']

    def get_sub_trainings(self, obj):
        sub_trainings = SubTraining.objects.filter(main_training=obj)
        return SubTrainingUpdateSerializer(sub_trainings, many=True).data

class EmployeeSearchSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'fullname', 'gate_pass_no', 'designation', 'company_name', 'project_name']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'created_at']

class AveragePercentageSerializer(serializers.Serializer):
    main_training_name = serializers.CharField()
    average_percentage = serializers.FloatField()


class URLSerializer(serializers.Serializer):
    name = serializers.CharField()
    pattern = serializers.CharField()

class EmployeeSubTrainingPDFUpdateSerializer(serializers.ModelSerializer):
    pdf = serializers.FileField(required=True)

    class Meta:
        model = EmployeeSubTraining
        fields = ['pdf']    