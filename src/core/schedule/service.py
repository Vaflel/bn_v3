from datetime import datetime

from src.core.schedule.parsers import RequestsScheduleParser, IndividualScheduleParser
from src.core.schedule.schemas import Lesson
from src.core.users.schemas import SUser
from src.core.schedule.schedule_builder import ScheduleBuilder
from src.core.schedule.image_creator import ImageCreator
from src.plugins.email_handler import EmailScheduleManager


class ScheduleService:
    def __init__(self, user_dto: SUser):
        self.user: SUser = user_dto

    def create_schedule(self) -> bytes:
        email = EmailScheduleManager()
        email.process_letters()
        parser = RequestsScheduleParser(
            department_name=self.user.department_name,
            group_name=self.user.group_name,
        )
        group_lessons = parser.parse()
        processed_group_lessons = self._process_group_lessons(group_lessons)

        if processed_group_lessons:
            first_lesson = processed_group_lessons[0]
            week_start_date = datetime.strptime(first_lesson.date.week_date_start, '%d.%m.%Y')
            week_end_date = datetime.strptime(first_lesson.date.week_date_end, '%d.%m.%Y')

            parser2 = IndividualScheduleParser()
            individual_lessons = parser2.parse()

            filtered_individual_lessons = [
                lesson for lesson in individual_lessons
                if week_start_date <= datetime.strptime(lesson.date.week_date_start, '%d.%m.%Y') <= week_end_date
            ]

            processed_ind_lessons = self._process_individual_lessons(filtered_individual_lessons)

            all_lessons = processed_group_lessons + processed_ind_lessons

            selected_lessons = []
            for lesson in all_lessons:
                if lesson.group == self.user.group_name and (
                        lesson.student == self.user.name or lesson.student is None):
                    selected_lessons.append(lesson)

            named_lessons = []
            for lesson in selected_lessons:
                lesson.student = self.user.name
                named_lessons.append(lesson)

            builder = ScheduleBuilder(named_lessons)
            schedule = builder.build()
            creator = ImageCreator(schedule)
            image = creator.generate_image()
            return image

    def _process_individual_lessons(self, lessons):
        doubled_lessons = []
        single_lessons = []
        for lesson in lessons:
            if lesson.discipline == "Вокал" or lesson.discipline == "Дирижирование":
                doubled_lessons.append(lesson)
            else:
                single_lessons.append(lesson)

        grouped_lessons = {}

        for lesson in doubled_lessons:
            key = (
                lesson.date,
                lesson.time.number,
                lesson.time.pair_half,
                lesson.discipline,
                lesson.cabinet,
                lesson.group,
                lesson.student
            )

            if key not in grouped_lessons:
                grouped_lessons[key] = {
                    'lesson': lesson,
                    'teachers': [lesson.teacher]
                }
            else:
                if lesson.teacher not in grouped_lessons[key]['teachers']:
                    grouped_lessons[key]['teachers'].append(lesson.teacher)

        deduplicated_lessons = []
        for key, value in grouped_lessons.items():
            if len(value['teachers']) == 2:
                teachers = " & ".join(value['teachers'])
                deduplicated_lesson = Lesson(
                    date=value['lesson'].date,
                    time=value['lesson'].time,
                    discipline=value['lesson'].discipline,
                    teacher=teachers,
                    cabinet=value['lesson'].cabinet,
                    group=value['lesson'].group,
                    student=value['lesson'].student
                )
                deduplicated_lessons.append(deduplicated_lesson)

        all_ind_lessons = single_lessons + deduplicated_lessons
        return all_ind_lessons

    def _process_group_lessons(self, lessons):
        return [lesson for lesson in lessons if lesson.discipline != 'Индивидуальные занятия /']


if __name__ == "__main__":
    user = SUser(
        id=836309692,
        name="Климанова П.",
        group_name="МД-21-о",
        department_name="Факультет искусств и физической культуры",
    )
    service = ScheduleService(user)
    image = service.create_schedule()
    with open("img.png", "wb") as f:
        f.write(image)
