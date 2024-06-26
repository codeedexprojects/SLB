from django.db import models
from datetime import timedelta, date

# Create your models here.

class Company(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Employee(models.Model):
    fullname = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15,unique=True)
    designation = models.CharField(max_length=100)
    gate_pass_no = models.CharField(max_length=50, unique=True)
    rig_or_rigless = models.CharField(max_length=50, choices=[('Rig', 'Rig'), ('Rigless', 'Rigless')])
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    on_duty = models.BooleanField(default=False)


    def __str__(self):
        return self.fullname
    
VALIDITY_CHOICES = [
    (timedelta(days=182), '6 months'),
    (timedelta(days=365), '1 year'),
    (timedelta(days=730), '2 years'),
    (timedelta(days=1095), '3 years'),
    (None, 'Permanent')
]

class MainTraining(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class SubTraining(models.Model):
    main_training = models.ForeignKey(MainTraining, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    VALIDITY_CHOICES = [
        (timedelta(days=182), '6 months'),
        (timedelta(days=365), '1 year'),
        (timedelta(days=365 * 2), '2 years'),
        (timedelta(days=365 * 3), '3 years'),
        (None, 'Permanent')
    ]
    validity_period = models.DurationField(choices=VALIDITY_CHOICES, null=True, blank=True)


class EmployeeSubTraining(models.Model):
    employee = models.ForeignKey(Employee, related_name='sub_trainings', on_delete=models.CASCADE)
    sub_training = models.ForeignKey(SubTraining, related_name='employee_sub_trainings', on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    warning = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.start_date:
            self.start_date = date.today()
        if self.sub_training.validity_period:
            self.expiration_date = self.start_date + self.sub_training.validity_period
        if self.expiration_date and (self.expiration_date - timedelta(days=30)) <= date.today():
            self.warning = True
        super().save(*args, **kwargs)

    def calculate_completion(self):
        if not self.sub_training.validity_period or not self.expiration_date:
            return 100.0  # Permanent training or invalid dates have 100% completion as a double
        total_duration = self.sub_training.validity_period
        elapsed_duration = date.today() - self.start_date
        completion_percentage = max(0, 100 - (elapsed_duration / total_duration) * 100)
        return round(completion_percentage, 2)

    def __str__(self):
        return f"{self.employee.fullname} - {self.sub_training.name}"
    

class Notification(models.Model):
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message