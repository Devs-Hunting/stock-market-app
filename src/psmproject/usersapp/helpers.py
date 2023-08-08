from typing import List

from .models import Skill


def skills_from_text(skills_str: List[str]) -> List[Skill]:
    skills = []
    for skill_str in skills_str:
        skill, created = Skill.objects.get_or_create(skill__iexact=skill_str, defaults={"skill": skill_str})
        skills.append(skill)

    return skills


def skills_to_text(skills: List[Skill]) -> List[str]:
    return [skill.skill for skill in skills]
