from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Employee, Notification

@receiver(post_save, sender=Employee)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(message=f"New employee registered: {instance.fullname}")