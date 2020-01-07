from random import random

import lorem

from trojsten.contests.models import Round, Task


class TaskGenerator:
    name_length = (1, 2)
    categories = []
    has_description = False
    description_points = 0
    has_source = False
    source_points = 0
    has_testable_zip = False
    integer_source_points = True

    @classmethod
    def generate(cls, parent_round: Round, number: int, **kwargs) -> Task:
        return Task.objects.create(
            round=parent_round,
            name=lorem.get_word(count=random.randint(*cls.name_length)),
            number=number,
            categories=kwargs.get("categories", cls.categories),
            has_description=kwargs.get("has_description", cls.has_description),
            description_points=kwargs.get("description_points", cls.description_points),
            has_source=kwargs.get("has_source", cls.has_source),
            source_points=kwargs.get("source_points", cls.source_points),
            has_testable_zip=kwargs.get("has_testable_zip", cls.has_testable_zip),
            integer_source_points=kwargs.get("integer_source_points", cls.integer_source_points),
        )


class KspTaskGenerator(TaskGenerator):
    has_description = True
    description_points = 12
    has_source = True
    source_points = 8
