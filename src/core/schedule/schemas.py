from dataclasses import dataclass
from datetime import datetime


@dataclass
class LessonDate:
    date: str
    day_name: str
    week_date_start: str
    week_date_end: str

    def __post_init__(self):
        # Преобразуем строку даты в объект datetime для удобства сравнения
        self.date_obj = datetime.strptime(self.date, '%d.%m.%Y')

    def __lt__(self, other):
        # Сравниваем по объекту даты
        return self.date_obj < other.date_obj

    def __eq__(self, other):
        # Сравниваем по объекту даты
        return self.date_obj == other.date_obj

    def __hash__(self):
        # Используем строку даты для вычисления хэша
        return hash(self.date)

@dataclass
class LessonTime:
    number: int
    pair_half: int
    start_time: str | None = None
    end_time: str | None = None

@dataclass
class Lesson:
    date: LessonDate
    time: LessonTime
    discipline: str
    teacher: str
    cabinet: str
    group: str
    student: str | None = None

@dataclass
class Pair:
    date: str
    time: LessonTime
    discipline: str
    teacher: str
    cabinet: str
    group: str
    student: str | None = None

@dataclass
class ScheduleDay:
    header: str
    pairs: list[Pair]


@dataclass
class WeekSchedule:
    group_name: str
    header: str
    days: list[ScheduleDay]
    student: str | None = None
