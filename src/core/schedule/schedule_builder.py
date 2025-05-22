from itertools import groupby

from src.core.schedule.schemas import Lesson, Pair, ScheduleDay, WeekSchedule, LessonTime


class ScheduleBuilder:
    def __init__(self, lessons):
        self.lessons: list[Lesson] = lessons
        self.pairs: list[Pair] = []
        self.days: list[ScheduleDay] = []

    def build(self) -> WeekSchedule:
        self._create_pairs()
        self._create_day_schedule()
        week_schedule = self._create_week_schedule()
        return week_schedule

    def _create_pairs(self):
        # Сортируем уроки для корректной группировки
        sorted_lessons = sorted(self.lessons, key=lambda l: (l.date, l.time.number, l.group, l.time.pair_half))


        # Группируем по дате, номеру пары и группе
        key_func = lambda l: (l.date, l.time.number, l.group)
        for key, group in groupby(sorted_lessons, key=key_func):
            group_lessons = list(group)
            # Сортируем по половине пары внутри группы
            sorted_group = sorted(group_lessons, key=lambda l: l.time.pair_half)

            # Обрабатываем случай, когда уроков меньше двух
            if len(sorted_group) == 1:
                lesson = sorted_group[0]
                # Создаем фиктивный урок для недостающей половины
                if lesson.time.pair_half == '1':
                    empty_time = LessonTime(
                        number=lesson.time.number,
                        pair_half='2',
                        start_time=lesson.time.start_time,
                        end_time=lesson.time.end_time
                    )
                    empty_lesson = Lesson(
                        date=lesson.date,
                        time=empty_time,
                        discipline='',
                        teacher='',
                        cabinet='',
                        group=lesson.group,
                        student=lesson.student
                    )
                    sorted_group.append(empty_lesson)
                else:
                    empty_time = LessonTime(
                        number=lesson.time.number,
                        pair_half='1',
                        start_time=lesson.time.start_time,
                        end_time=lesson.time.end_time
                    )
                    empty_lesson = Lesson(
                        date=lesson.date,
                        time=empty_time,
                        discipline='',
                        teacher='',
                        cabinet='',
                        group=lesson.group,
                        student=lesson.student
                    )
                    sorted_group.insert(0, empty_lesson)

            # Извлекаем два урока (возможно, один из них фиктивный)
            lesson1, lesson2 = sorted_group[0], sorted_group[1]

            # Проверяем, совпадают ли дисциплина, преподаватель и кабинет
            same_discipline = (lesson1.discipline == lesson2.discipline)
            same_teacher = (lesson1.teacher == lesson2.teacher)
            same_cabinet = (lesson1.cabinet == lesson2.cabinet)

            if same_discipline and same_teacher and same_cabinet:
                discipline = lesson1.discipline
                teacher = lesson1.teacher
                cabinet = lesson1.cabinet
            else:
                discipline = f"{lesson1.discipline} / {lesson2.discipline}"
                teacher = f"{lesson1.teacher} / {lesson2.teacher}"
                cabinet = f"{lesson1.cabinet} / {lesson2.cabinet}"

            # Создаем объект Pair на основе первого урока в группе
            pair = Pair(
                date=lesson1.date,
                time=lesson1.time,
                discipline=discipline,
                teacher=teacher,
                cabinet=cabinet,
                group=lesson1.group,
                student=lesson1.student
            )
            self.pairs.append(pair)


    def _create_day_schedule(self):
        day_dict = {}
        for pair in self.pairs:
            date = pair.date
            if date not in day_dict:
                day_dict[date] = []
            day_dict[date].append(pair)

        for date, pairs in day_dict.items():
            self.days.append(ScheduleDay(header=f"{date.date}, {date.day_name}", pairs=pairs))

    def _create_week_schedule(self) -> WeekSchedule:
        group_name = self.days[0].pairs[0].group if self.days and self.days[0].pairs else "Неизвестная группа"
        if self.days and self.days[0].pairs and self.days[0].pairs[0].student:
            student_name = self.days[0].pairs[0].student
        else:
            student_name = ""
        header = f"Расписание на неделю для группы {group_name} ({student_name})"
        return WeekSchedule(group_name=group_name, header=header, days=self.days, student=student_name)
