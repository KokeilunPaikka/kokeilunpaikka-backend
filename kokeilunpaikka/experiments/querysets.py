from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils import timezone

from parler.managers import TranslatableQuerySet


class ExperimentQuerySet(QuerySet):

    def active(self):
        return self.filter(is_published=True)

    def for_user(self, user):
        """Return experiments user is eligible to see.

        Only responsible users of the experiment can see it before publication.
        """

        if user.id is None:
            return self.filter(is_published=True)

        return self.filter(
            Q(is_published=True) |
            Q(responsible_users__id=user.id)
        ).distinct()


class ExperimentChallengeQuerySet(TranslatableQuerySet):

    def active(self):
        now = timezone.now()
        return self.filter(
            Q(starts_at__lte=now) | Q(starts_at__isnull=True),
            Q(ends_at__gte=now) | Q(ends_at__isnull=True),
            is_visible=True,
        ).distinct()

    def visible(self):
        return self.filter(is_visible=True)
