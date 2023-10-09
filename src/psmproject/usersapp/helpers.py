from typing import List

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from .models import Skill


def skills_from_text(skills_str: List[str], create: bool = False) -> List[Skill]:
    skills = []
    for skill_str in skills_str:
        if create:
            skill, created = Skill.objects.get_or_create(skill__iexact=skill_str, defaults={"skill": skill_str})
        else:
            skill = Skill.objects.filter(skill__iexact=skill_str).first()
        if skill:
            skills.append(skill)

    return skills


def skills_to_text(skills: List[Skill]) -> List[str]:
    return [skill.skill for skill in skills]


class ModeratorMixin(UserPassesTestMixin):
    """
    Mixin to check if user has moderator rights
    """

    allowed_groups = [
        settings.GROUP_NAMES.get("ADMINISTRATOR"),
        settings.GROUP_NAMES.get("ARBITER"),
        settings.GROUP_NAMES.get("MODERATOR"),
    ]
    redirect_url = reverse_lazy("dashboard")

    def test_func(self):
        user = self.request.user
        in_allowed_group = user.groups.filter(name__in=self.allowed_groups).exists()
        return in_allowed_group

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseRedirect(self.redirect_url)
