from datetime import datetime, timedelta
from typing import Optional

from trojsten.contests.models import Round, Semester

from .task import KspTaskGenerator, TaskGenerator


class RoundGenerator:
    task_list = []
    task_generator: Optional[TaskGenerator] = None
    round_length: timedelta = timedelta(5 * 7)
    second_round_length: Optional[timedelta] = None
    visible = True
    solutions_visible = False
    results_final = False

    @classmethod
    def generate(
        cls, parent_semester: Semester, number: int, start_time: datetime, **kwargs
    ) -> Round:

        if cls.task_generator is None:
            raise NotImplementedError(
                "{}: You must override either 'task_generator' or 'generate'".format(cls.__name__)
            )

        round_length: timedelta = kwargs.get("round_length", cls.round_length)
        second_round_length = kwargs.get("second_round_length", cls.second_round_length)

        new_round = Round.objects.create(
            semester=parent_semester,
            number=number,
            start_time=start_time,
            end_time=start_time + round_length,
            second_end_time=None
            if second_round_length is None
            else start_time + second_round_length,
            visible=kwargs.get("visible", cls.visible),
            solutions_visible=kwargs.get("solutions_visible", cls.solutions_visible),
            results_final=kwargs.get("results_final", cls.results_final),
        )

        for number, params in enumerate(cls.task_list, start=1):
            cls.task_generator.generate(parent_round=new_round, number=number, **params)

        return new_round


class KspRoundGenerator(RoundGenerator):
    task_count = 8
    task_list = [dict() for _ in range(8)]
    task_generator = KspTaskGenerator
    second_round_length = timedelta(7 * 7)
