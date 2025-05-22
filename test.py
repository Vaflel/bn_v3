from datetime import datetime

import httpx
import json
from bs4 import BeautifulSoup

from config import settings
from src.core.schedule.schemas import LessonTime, LessonDate, Lesson


class RequestsScheduleParser:
    def __init__(self, department_name: str, group_name: str):
        self.department_name = department_name
        self.group_name = group_name
        self.client = httpx.Client()
        self.lessons = []

        self.client.headers.update(settings.REQ_HEADERS)

    def parse(self):
        lessons_data = self._get_lessons_data()
        group_lessons = []
        for lesson in lessons_data:
            extractor = ScheduleDataExtractor(lesson)
            lesson_objects = extractor.extract()
            for lesson_obj in lesson_objects:
                group_lessons.append(lesson_obj)
        return group_lessons

    def _get_lessons_data(self):
        main_page_resp = self.client.get(f'{settings.SCHEDULE_URL}?alias=429')
        main_soup = BeautifulSoup(main_page_resp.text, "html.parser")
        departments_codes = self._cut_departments_codes(main_soup)
        department_value = departments_codes.get(self.department_name)
        department_id = {
            'FakultetId': (None, str(department_value)),
        }

        group_code_resp = self.client.post(f'{settings.SCHEDULE_URL}plugins/AutoRasp/SearchGroup.php',
                                            files=department_id)
        group_codes_soup = BeautifulSoup(group_code_resp.text, 'html.parser')
        group_codes = self._cut_groups_codes(group_codes_soup)
        group_value = group_codes.get(self.group_name)

        group_id = {
            'GroupId': (None, str(group_value)),
        }

        schedule_data_resp = self.client.post(f'{settings.SCHEDULE_URL}plugins/AutoRasp/GroupLessonList.php',
                                               data=group_id)
        lessons = json.loads(schedule_data_resp.text)['LessonList'].values()
        return lessons

    def _cut_departments_codes(self, soup):
        label = soup.find('label', {'for': 'ChangeFakultet'})
        departments_codes = {}
        if label:
            select = label.find_next('select')
            if select:
                for option in select.find_all('option'):
                    option_text = option.get_text(strip=True)
                    option_value = option['value']
                    departments_codes[option_text] = option_value
        return departments_codes

    def _cut_groups_codes(self, soup):
        group_codes = {}
        for option in soup.find_all('option'):
            key = option.text.strip()
            value = option['value']
            group_codes[key] = value
        return group_codes

class ScheduleDataExtractor:
    def __init__(self, data):
        self.data = data

        self.days_of_week = {
            1: "понедельник",
            2: "вторник",
            3: "среда",
            4: "четверг",
            5: "пятница",
            6: "суббота",
            7: "воскресенье"
        }

    def extract(self):
        date, day_name, week_date_start, week_date_end = self._cut_date()
        lesson_number, start_time, end_time = self._cut_time()
        discipline_name = self._cut_discipline()
        if discipline_name == "Индивидуальные занятия":
            return []
        teacher_name = self._cut_teacher()
        cabinet_number = self._cut_cabinet()
        group_name = self._cut_group()

        lessons = []

        for pair_half in [1, 2]:
            lesson = Lesson(
                date=LessonDate(
                    date = date,
                    day_name = day_name,
                    week_date_start = week_date_start,
                    week_date_end = week_date_end,
                ),
                time=LessonTime(
                    number=lesson_number,
                    pair_half=pair_half,
                    start_time=start_time,
                    end_time=end_time,
                ),
                discipline=discipline_name,
                teacher=teacher_name,
                cabinet=cabinet_number,
                group=group_name,
            )
            lessons.append(lesson)
        return lessons

    def _cut_date(self):
        format_date = lambda d: datetime.strptime(d, "%Y-%m-%d").strftime("%d.%m.%Y")

        day_num = self.data.get("WEEK_DAY_NUM")
        day_name = self.days_of_week.get(day_num)

        date = format_date(self.data.get("WEEK_DAY_DATE"))
        week_date_start = format_date(self.data.get("WEEK_DATE_START"))
        week_date_end = format_date(self.data.get("WEEK_DATE_END"))

        return date, day_name, week_date_start, week_date_end

    def _cut_time(self):
        number = self.data.get("LESSON_NUM")
        start_time = self.data.get("LESSON_TIME_START")
        end_time = self.data.get("LESSON_TIME_END")

        return number, start_time, end_time

    def _cut_discipline(self):
        discipline = self.data.get("DISC_NAME")
        disc_type = self.data.get("DISC_TYPE")

        if disc_type == "":
            return discipline
        else:
            return f"{discipline} [{disc_type}]"

    def _cut_teacher(self):
        teacher = self.data.get("TEACHER_NAME")
        return teacher

    def _cut_cabinet(self):
        cabinet = self.data.get("AUDIT_NAME")
        return cabinet

    def _cut_group(self):
        group_name = self.data.get("GROUP_NAME")
        return group_name

if __name__ == "__main__":
    parser = RequestsScheduleParser(
        department_name="Факультет искусств и физической культуры",
        group_name="МД-24-о",
    )
    group_lessons = parser.parse()
    for lesson in group_lessons:
        print(lesson.discipline)
