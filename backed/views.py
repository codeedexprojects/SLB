# backed/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from .models import Company, Employee,MainTraining, SubTraining,EmployeeSubTraining,Project,Notification
from .serializers import CompanySerializer, EmployeeSerializer, EmployeePhotoSerializer,MainTrainingCreateUpdateSerializer,MainTrainingSerializer,SubTrainingSerializer\
,EmployeeSubTrainingSerializer,AdminLoginSerializer,ProjectsSerializer,AcceptRejectEmployeeSerializer,OnDutyOffDutyToggleSerializer,EmployeePercentageSubTrainingSerializer\
,MainTrainingsSerializer,SubTrainingWithMainNameSerializer,MainTrainingWithSubSerializer,EmployeeSearchSerializer,EmployeeMainTrainingSerializer,NotificationSerializer\
,AverageCompletionPercentageSerializer,AveragePercentageSerializer,SubTrainingUpdateSerializer,URLSerializer,EmployeeSubTrainingPDFUpdateSerializer
from rest_framework.views import APIView
from django.contrib.auth import login
from .filters import EmployeeFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser
from django.urls import get_resolver
from rest_framework.permissions import IsAdminUser


# Company Views
class CompanyListCreateView(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class CompanyRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

# Employee Views
class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class EmployeeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

@api_view(['POST'])
def EmployeeLoginView(request):
    fullname = request.data.get('fullname')
    mobile_number = request.data.get('mobile_number')
    
    if not fullname or not mobile_number:
        return Response(
            {
                "status": False,
                "error": "fullname and mobile_number are required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        employee = get_object_or_404(Employee, fullname=fullname, mobile_number=mobile_number)
        serializer = EmployeeSerializer(employee)
        return Response(
            {
                "status": True,
                "message": "Login successful",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {
                "status": False,
                "error": str(e)
            },
            status=status.HTTP_404_NOT_FOUND
        )

class EmployeeUpdatePhotoView(generics.UpdateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeePhotoSerializer


class MainTrainingListCreateView(generics.ListCreateAPIView):
    queryset = MainTraining.objects.all()
    serializer_class = MainTrainingCreateUpdateSerializer

class MainTrainingRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = MainTraining.objects.all()
    serializer_class = MainTrainingCreateUpdateSerializer

# Sub Training Views
class SubTrainingListCreateView(generics.ListCreateAPIView):
    queryset = SubTraining.objects.all()
    serializer_class = SubTrainingSerializer

class SubTrainingRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = SubTraining.objects.all()
    serializer_class = SubTrainingUpdateSerializer

class EmployeeSubTrainingListCreateView(generics.ListCreateAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = EmployeeSubTraining.objects.all()
    serializer_class = EmployeeSubTrainingSerializer


class EmployeeSubTrainingDeleteView(generics.DestroyAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = EmployeeSubTrainingSerializer
    lookup_url_kwarg = 'subtraining_id'

    def get_queryset(self):
        employee_id = self.kwargs['employee_id']
        return EmployeeSubTraining.objects.filter(employee_id=employee_id)

    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        subtraining_id = self.kwargs.get(self.lookup_url_kwarg)
        instance = queryset.filter(sub_training_id=subtraining_id).first()
        if instance:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Employee sub-training not found."}, status=status.HTTP_404_NOT_FOUND)


class EmployeeSubTrainingRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = EmployeeSubTraining.objects.all()
    serializer_class = EmployeeSubTrainingSerializer



# Retrieve a single employee by ID
class EmployeeDetailView(generics.RetrieveAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

# List all companies with their names and IDs
class CompanyListView(generics.ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class MainTrainingsListView(generics.ListAPIView):
    queryset = MainTraining.objects.all()
    serializer_class = MainTrainingsSerializer

# List all main trainings with their sub-trainings
class MainTrainingWithSubTrainingsListView(generics.ListAPIView):
    queryset = MainTraining.objects.all()
    serializer_class = MainTrainingSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs, many=True)



class AverageCompletionPercentageView(APIView):
    def get(self, request, employee_id):
        employee = get_object_or_404(Employee, id=employee_id)
        sub_trainings = EmployeeSubTraining.objects.filter(employee=employee)

        if not sub_trainings.exists():
            return Response({"detail": "No sub-trainings found for this employee."}, status=status.HTTP_404_NOT_FOUND)

        total_percentage = sum([sub_training.calculate_completion() for sub_training in sub_trainings])
        average_percentage = total_percentage / sub_trainings.count()

        data = {
            'employee_id': employee.id,
            'average_completion_percentage': round(average_percentage, 2)
        }

        serializer = AverageCompletionPercentageSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Retrieve, update, or delete a single employee sub-training by ID
class EmployeeSubTrainingRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EmployeeSubTraining.objects.all()
    serializer_class = EmployeeSubTrainingSerializer

class EmployeeSubTrainingListView(generics.ListAPIView):
    serializer_class = EmployeePercentageSubTrainingSerializer

    def get_queryset(self):
        employee_id = self.kwargs['employee_id']
        return EmployeeSubTraining.objects.filter(employee__id=employee_id)

class EmployeeMainTrainingDetailView(generics.ListAPIView):
    serializer_class = EmployeeMainTrainingSerializer

    def get_queryset(self):
        employee_id = self.kwargs['employee_id']
        main_training_id = self.kwargs['main_training_id']
        return EmployeeSubTraining.objects.filter(
            employee__id=employee_id,
            sub_training__main_training__id=main_training_id
        )

class EmployeeMainTrainingAverageView(APIView):

    def get(self, request, employee_id, main_training_id):
        sub_trainings = EmployeeSubTraining.objects.filter(
            employee__id=employee_id,
            sub_training__main_training__id=main_training_id
        )

        if not sub_trainings.exists():
            return Response({'error': 'No sub-trainings found for the given employee and main training'}, status=status.HTTP_404_NOT_FOUND)

        total_percentage = sum(sub_training.calculate_completion() for sub_training in sub_trainings)
        average_percentage = total_percentage / sub_trainings.count()

        data = {
            'main_training_name': sub_trainings.first().sub_training.main_training.name,
            'average_percentage': round(average_percentage, 2)
        }
        serializer = AveragePercentageSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminLoginView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request, *args, **kwargs):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({
                "detail": "Login successful",
                "id": user.id
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectListView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectsSerializer

class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectsSerializer

class ProjectUpdateView(generics.UpdateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectsSerializer

class ProjectDeleteView(generics.DestroyAPIView):
    queryset = Project.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Project deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectsSerializer

class EmployeeListView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class AcceptRejectEmployeeView(generics.UpdateAPIView):
    queryset = Employee.objects.all()
    serializer_class = AcceptRejectEmployeeSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action = serializer.validated_data['action']
        
        if action == 'reject':
            instance.delete()
            return Response({"message": "Employee rejected and deleted."}, status=status.HTTP_204_NO_CONTENT)
        
        instance.is_accepted = True
        instance.save()
        return Response(EmployeeSerializer(instance).data)


# List all accepted employees
class AcceptedEmployeeListView(generics.ListAPIView):
    queryset = Employee.objects.filter(is_accepted=True)
    serializer_class = EmployeeSerializer

# List all not accepted employees
class NotAcceptedEmployeeListView(generics.ListAPIView):
    queryset = Employee.objects.filter(is_accepted=False)
    serializer_class = EmployeeSerializer


class OnDutyOffDutyToggleView(generics.UpdateAPIView):
    queryset = Employee.objects.all()
    serializer_class = OnDutyOffDutyToggleSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
class OnDutyEmployeeListView(generics.ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmployeeFilter

    def get_queryset(self):
        return Employee.objects.filter(on_duty=True)
    

class OfDutyEmployeeListView(generics.ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmployeeFilter

    def get_queryset(self):
        return Employee.objects.filter(on_duty=False)

class EmployeeSearchAPIView(generics.ListAPIView):
    serializer_class = EmployeeSearchSerializer

    def get_queryset(self):
        queryset = Employee.objects.filter(is_accepted=True)
        fullname = self.request.query_params.get('fullname', None)
        gate_pass_no = self.request.query_params.get('gate_pass_no', None)
        designation = self.request.query_params.get('designation', None)
        company_name = self.request.query_params.get('company_name', None)
        project_name = self.request.query_params.get('project_name', None)

        if fullname:
            queryset = queryset.filter(fullname__icontains=fullname)
        if gate_pass_no:
            queryset = queryset.filter(gate_pass_no__icontains=gate_pass_no)
        if designation:
            queryset = queryset.filter(designation__icontains=designation)
        if company_name:
            queryset = queryset.filter(company__name__icontains=company_name)
        if project_name:
            queryset = queryset.filter(project__name__icontains=project_name)

        return queryset
    
class ProjectListView(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectsSerializer

class CompanyListView(generics.ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class SubTrainingListView(generics.ListAPIView):
    queryset = SubTraining.objects.all()
    serializer_class = SubTrainingWithMainNameSerializer



class MainTrainingListView(generics.ListAPIView):
    queryset = MainTraining.objects.all()
    serializer_class = MainTrainingWithSubSerializer


class NotificationListView(generics.ListAPIView):
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer

class NotificationDetailView(generics.RetrieveDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer



class EmployeeSubTrainingUploadView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = EmployeeSubTraining.objects.all()
    serializer_class = EmployeeSubTrainingSerializer
    parser_classes = (MultiPartParser, FormParser)

class EmployeeSubTrainingUpdateView(generics.UpdateAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = EmployeeSubTraining.objects.all()
    serializer_class = EmployeeSubTrainingSerializer
    parser_classes = (MultiPartParser, FormParser)

class SubTrainingListByMainTrainingView(generics.ListAPIView):
    serializer_class = SubTrainingSerializer

    def get_queryset(self):
        main_training_id = self.kwargs['main_training_id']
        return SubTraining.objects.filter(main_training_id=main_training_id)
    
class URLListView(APIView):

    def get(self, request, *args, **kwargs):
        url_patterns = get_resolver().url_patterns
        data = []

        def parse_patterns(patterns, parent_pattern=''):
            for pattern in patterns:
                if hasattr(pattern, 'url_patterns'):
                    parse_patterns(pattern.url_patterns, parent_pattern + str(pattern.pattern))
                else:
                    data.append({
                        'name': pattern.name,
                        'pattern': parent_pattern + str(pattern.pattern)
                    })

        parse_patterns(url_patterns)
        serializer = URLSerializer(data=data, many=True)
        serializer.is_valid()  # To initialize and format the data
        return Response(serializer.data)



class EmployeesSubTrainingListView(generics.ListAPIView):
    serializer_class = EmployeeSubTrainingSerializer

    def get_queryset(self):
        employee_id = self.kwargs['employee_id']
        return EmployeeSubTraining.objects.filter(employee_id=employee_id)
    
from django.http import HttpResponse, Http404


class EmployeeSubTrainingPDFView(APIView):

    def get(self, request, employee_id, sub_training_id, format=None):
        try:
            sub_training = EmployeeSubTraining.objects.get(employee_id=employee_id, sub_training_id=sub_training_id)
        except EmployeeSubTraining.DoesNotExist:
            raise Http404

        if not sub_training.pdf:
            raise Http404

        response = HttpResponse(sub_training.pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{sub_training.pdf.name}"'
        return response
    
from rest_framework.generics import UpdateAPIView


class EmployeeSubTrainingPDFUpdateView(generics.UpdateAPIView):
    queryset = EmployeeSubTraining.objects.all()
    serializer_class = EmployeeSubTrainingPDFUpdateSerializer
    authentication_classes = []
    permission_classes = []

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
class VerifyPDFView(generics.UpdateAPIView):
    queryset = EmployeeSubTraining.objects.all()
    serializer_class = EmployeeSubTrainingSerializer
    authentication_classes = []
    permission_classes = []

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        verify_pdf = request.data.get('verify_pdf')

        if verify_pdf is not None:
            instance.verify_pdf = verify_pdf
            instance.save()
            return Response({'status': 'PDF verification updated'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)