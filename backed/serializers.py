from rest_framework import serializers
from .models import Company, Employee,MainTraining, SubTraining,EmployeeSubTraining,Project,Notification
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from datetime import timedelta, date

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
        'Permanent': None,
    }

    validity_period = serializers.ChoiceField(choices=list(VALIDITY_CHOICES.keys()))

    class Meta:
        model = SubTraining
        fields = ['main_training', 'name', 'validity_period']

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

class MainTrainingSerializer(serializers.ModelSerializer):
    # sub_trainings = SubTrainingSerializer(many=True, read_only=True)

    class Meta:
        model = MainTraining
        fields = '__all__'

class MainTrainingCreateUpdateSerializer(serializers.ModelSerializer):
    # sub_trainings = SubTrainingSerializer(many=True)

    class Meta:
        model = MainTraining
        fields = ['id', 'name']

    # def create(self, validated_data):
    #     # sub_trainings_data = validated_data.pop('sub_trainings')
    #     main_training = MainTraining.objects.create(**validated_data)
    #     # for sub_training_data in sub_trainings_data:
    #     #     SubTraining.objects.create(main_training=main_training, **sub_training_data)
    #     # return main_training

    def update(self, instance, validated_data):
        sub_trainings_data = validated_data.pop('sub_trainings')
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        # Delete existing sub-trainings and create new ones
        instance.sub_trainings.all().delete()
        for sub_training_data in sub_trainings_data:
            SubTraining.objects.create(main_training=instance, **sub_training_data)

        return instance
    

class EmployeeSubTrainingSerializer(serializers.ModelSerializer):
    start_date = CustomDateField(required=False)
    expiration_date = CustomDateField(required=False)  # expiration_date might not always be set

    class Meta:
        model = EmployeeSubTraining
        fields = ['employee', 'sub_training', 'start_date', 'expiration_date', 'warning']

    def validate(self, attrs):
        # Set default value for start_date if not provided
        if 'start_date' not in attrs or attrs['start_date'] is None:
            attrs['start_date'] = date.today()
        return attrs

    def create(self, validated_data):
        sub_training = validated_data['sub_training']
        start_date = validated_data['start_date']
        expiration_date = None

        if sub_training.validity_period:
            expiration_date = start_date + sub_training.validity_period

        validated_data['expiration_date'] = expiration_date

        # Create the EmployeeSubTraining instance
        employee_sub_training = EmployeeSubTraining.objects.create(**validated_data)

        # Check and set the warning flag
        if expiration_date and (expiration_date - timedelta(days=30)) <= date.today():
            employee_sub_training.warning = True
            employee_sub_training.save()

        return employee_sub_training
    
class AverageCompletionPercentageSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    average_completion_percentage = serializers.FloatField()

class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if user:
                if not user.is_superuser:
                    raise serializers.ValidationError("User does not have admin privileges.")
                data['user'] = user
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")

        return data

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

    class Meta:
        model = EmployeeSubTraining
        fields = ['employee_name', 'main_training_name', 'sub_training_name', 'start_date', 'expiration_date', 'warning', 'completion_percentage']

    def get_completion_percentage(self, obj):
        return obj.calculate_completion()
    
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
        return SubTrainingSerializer(sub_trainings, many=True).data


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