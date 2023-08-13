from django.test import TestCase
from usersapp.helpers import skills_from_text, skills_to_text
from usersapp.models import Skill


class TestSkillsFromText(TestCase):
    """
    Test helper function skills_from_text for Skill model
    """

    def setUp(self):
        self.skills_str = ["python", "java", "django"]

    def test_should_return_list_of_skill_instances(self):
        """
        Test that checks if helper function return correct list of skills instances given list of skills strings
        """
        skills = skills_from_text(self.skills_str)
        self.assertIsInstance(skills, list)
        index = 0
        for skill in skills:
            self.assertIsInstance(skill, Skill)
            self.assertEqual(skill.skill, self.skills_str[index])
            index += 1

    def test_should_return_empty_list_if_no_skills_as_string_are_given(self):
        """
        Test that checks if helper function return empty list if empty list of skills strings given
        """
        skills = skills_from_text([])
        self.assertListEqual(skills, [])

    def test_should_not_overwrite_existing_skills(self):
        """
        Test that checks if helper function is not createing new skill object if the skill already exists
        """
        existing_index = 0
        existing = Skill.objects.create(skill=self.skills_str[existing_index])
        skills = skills_from_text(self.skills_str)

        self.assertEqual(existing.id, skills[existing_index].id)


class TestSkillsToText(TestCase):
    def setUp(self):
        self.skills_str = ["python", "java", "django"]

    def test_should_return_list_of_strings(self):
        """
        Test that checks if the helper function returns correct list of strings given list of skill objects
        """
        test_skills = []
        for test_string in self.skills_str:
            test_skills.append(Skill.objects.create(skill=test_string))

        skills_as_string = skills_to_text(test_skills)

        self.assertIsInstance(skills_as_string, list)
        index = 0
        for skill in skills_as_string:
            self.assertIsInstance(skill, str)
            self.assertEqual(skill, test_skills[index].skill)
            index += 1

    def test_should_return_empty_list_if_empty_list_given_as_parameter(self):
        """
        Test that checks if the helper function returns empty list if empty list given as parameter
        """

        skills_as_string = skills_to_text([])
        self.assertListEqual(skills_as_string, [])
