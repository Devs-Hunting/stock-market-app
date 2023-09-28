from typing import List

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
