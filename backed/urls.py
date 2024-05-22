from django.urls import path
from backed import views
from .views import EmployeeLoginView


urlpatterns = [
    # Company URLs
    path('create-companies/', views.CompanyListCreateView.as_view(), name='company-list-create'),
    path('companies/<int:pk>/', views.CompanyRetrieveUpdateDestroyView.as_view(), name='company-detail'),
    path('viewcompanies/', views.CompanyListView.as_view(), name='company-list'),

    
    # Employee URLs
    path('register-employees/', views.EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('employees/<int:pk>/', views.EmployeeRetrieveUpdateDestroyView.as_view(), name='employee-detail'),
    path('employees/', views.EmployeeListView.as_view(), name='employee-list'),
    path('employees-login/', EmployeeLoginView, name='employee-login'),
    path('employees/<int:pk>/update-photo/', views.EmployeeUpdatePhotoView.as_view(), name='employee-update-photo'),
    path('employees/<int:pk>/accept-reject/', views.AcceptRejectEmployeeView.as_view(), name='accept-reject-employee'),
    path('employees-accepted/', views.AcceptedEmployeeListView.as_view(), name='accepted-employee-list'),
    path('employees-not-accepted/', views.NotAcceptedEmployeeListView.as_view(), name='not-accepted-employee-list'),
    path('employees/<int:pk>/toggle-duty/', views.OnDutyOffDutyToggleView.as_view(), name='toggle-duty'),
    path('employees/on-duty/', views.OnDutyEmployeeListView.as_view(), name='on-duty-employees'),
    path('employees/off-duty/', views.OfDutyEmployeeListView.as_view(), name='of-duty-employees'),
    path('employees/search/', views.EmployeeSearchAPIView.as_view(), name='employee-search'),
    path('employeetrainingpercentage/<int:employee_id>/', views.EmployeeSubTrainingListView.as_view(), name='employee-sub-trainings'),
    path('employee/<int:employee_id>/main-training/<int:main_training_id>/', views.EmployeeMainTrainingDetailView.as_view(), name='employee-main-training-detail'),
    path('employees/<int:employee_id>/average-completion-percentage/', views.AverageCompletionPercentageView.as_view(), name='average-completion-percentage'),
    path('employee/<int:employee_id>/main-training/<int:main_training_id>/average/', views.EmployeeMainTrainingAverageView.as_view(), name='employee-main-training-average'),

    
    

     # Main Training URLs
    path('main-trainings/', views.MainTrainingListCreateView.as_view(), name='main-training-list-create'),
    path('main-trainings/<int:pk>/', views.MainTrainingRetrieveUpdateDestroyView.as_view(), name='main-training-detail'),
    path('view-main-trainings/', views.MainTrainingListView.as_view(), name='main-training-list'),

    
    # Sub Training URLs
    path('sub-trainings/', views.SubTrainingListCreateView.as_view(), name='sub-training-list-create'),
    path('sub-trainings/<int:pk>/', views.SubTrainingRetrieveUpdateDestroyView.as_view(), name='sub-training-detail'),
    path('sub-trainings-main/', views.SubTrainingListView.as_view(), name='sub-training-list'),


    # Employee SubTraining URLs
    path('employee-sub-trainings/', views.EmployeeSubTrainingListCreateView.as_view(), name='employee-sub-training-list-create'),
    path('employee-sub-trainings/<int:pk>/', views.EmployeeSubTrainingRetrieveUpdateDestroyView.as_view(), name='employee-sub-training-detail'),
    path('employees/<int:employee_id>/subtrainings/<int:subtraining_id>/', views.EmployeeSubTrainingDeleteView.as_view(), name='employee-subtraining-delete'),


    # Admin Login URLs
    path('adminlogin/', views.AdminLoginView.as_view(), name='admin-login'),

    # Projects URLs
    path('create-project/', views.ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('viewprojects/', views.ProjectListView.as_view(), name='project-list'),
    path('updateprojects/<int:pk>/', views.ProjectUpdateView.as_view(), name='project-update'),
    path('delprojects/<int:pk>/', views.ProjectDeleteView.as_view(), name='project-delete'),

    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('del-notifications/<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),





]