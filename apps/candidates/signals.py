
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import User
from apps.candidates.models import CandidateProfile


@receiver(post_save, sender=User)
def create_candidate_profile(sender, instance, created, **kwargs):

    if created and instance.role == 'STUDENT':

        CandidateProfile.objects.get_or_create(
            user=instance
        )
