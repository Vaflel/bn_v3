import json
import os
import re
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
import xlrd

from src.core.schedule.schemas import Lesson, LessonTime, LessonDate
from config import settings


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



class IndividualScheduleParser:
    def __init__(self):
        self.file_paths = []
        self.pair_time = {
            1: ("08:30", "10:00"),
            2: ("10:10", "11:40"),
            3: ("11:50", "13:20"),
            4: ("13:40", "15:10"),
            5: ("15:20", "16:50"),
            6: ("16:55", "18:25"),
            7: ("18:30", "20:00"),
        }

    def parse(self):
        self._load_file_paths()
        all_ind_lessons = []

        for file_path in self.file_paths:
            workbook = xlrd.open_workbook(file_path)
            sheet = workbook.sheet_by_index(2)  # Предполагаем, что нужные данные на третьем листе
            ind_lessons = []

            teachers_list = []
            for row_index in range(sheet.nrows):
                if sheet.cell_value(row_index, 5) == "Расписание индивидуальных занятий":
                    teachers_list.append(row_index)

            for teacher_table_row in teachers_list:
                teacher_name = self._cut_teacher(sheet, teacher_table_row)
                days_columns = self._get_days_columns(sheet, teacher_table_row)
                lessons_row_start = teacher_table_row + 8

                for day_column in days_columns:
                    for lesson_row in range(lessons_row_start, sheet.nrows):
                        date, day_name, week_date_start, week_date_end = self._cut_date(sheet, lessons_row_start, day_column)
                        lesson_number = self._cut_time(sheet, lesson_row, 1)
                        if lesson_number is None:
                            break
                        discipline_name = self._cut_discipline(sheet, lesson_row, day_column)
                        cabinet_number = self._cut_cabinet(sheet, lesson_row, day_column)
                        group_name = self._cut_group(sheet, lesson_row, day_column)
                        student_names = self._cut_student_name(sheet, lesson_row, day_column)

                        for index, student_name in enumerate(student_names):
                            group_name = None if student_name is None else group_name

                            lesson = Lesson(
                                date=LessonDate(
                                    date=date,
                                    day_name=day_name,
                                    week_date_start=week_date_start,
                                    week_date_end=week_date_end,
                                ),
                                time=LessonTime(
                                    number=lesson_number,
                                    pair_half=(index + 1),
                                    start_time=self.pair_time.get(lesson_number)[0],
                                    end_time=self.pair_time.get(lesson_number)[1],
                                ),
                                discipline=discipline_name,
                                teacher=teacher_name,
                                cabinet=cabinet_number,
                                group=group_name,
                                student=student_name,
                            )
                            ind_lessons.append(lesson)
            all_ind_lessons.extend(ind_lessons)
        return all_ind_lessons

    def _cut_date(self, sheet, lessons_row_start, day_col):
        days_header_row = lessons_row_start - 3
        day_name = sheet.cell_value(days_header_row, day_col)
        period_row = sheet.cell_value(days_header_row - 2, 7)
        current_year = re.findall(r'\b(\d{4})\b', period_row)[0]

        pattern = r'(\d{2}\.\d{2}\.\d{4})\s+г\.\s+по\s+(\d{2}\.\d{2}\.\d{4})\s+г\.'
        match = re.search(pattern, period_row)
        week_date_start = match.group(1)
        week_date_end = match.group(2)

        date_row = sheet.cell_value(days_header_row + 1, day_col)
        date_str = re.sub(r'Дата:\s*', '', date_row)
        date = f"{date_str}{current_year}"

        return date, day_name, week_date_start, week_date_end

    def _cut_time(self, sheet, row, column):
        lesson_number = sheet.cell_value(row, column)
        if isinstance(lesson_number, (int, float)):
            return int(lesson_number)
        else:
            return None

    def _cut_discipline(self, sheet, row, column):
        discipline_data = sheet.cell_value(row, column + 1)
        discipline_data = ' '.join(discipline_data.split())
        pattern = r"^\S+"
        match = re.match(pattern, discipline_data)
        if not match:
            return None

        discipline_name = match.group(0)
        if discipline_name in ["Дир.хор.подг.", "Хор.дир."]:
            output_data = "Дирижирование"
        elif discipline_name in ["Муз.инстр.испол.", "Муз.инстр.подгот.", "Муз.инстр.подготов."]:
            output_data = "Муз. Инструмент"
        elif discipline_name == "Вокал.":
            output_data = "Вокал"
        else:
            output_data = discipline_name

        return output_data

    def _cut_teacher(self, sheet, teacher_table_row):
        teacher_name_row = sheet.cell_value(teacher_table_row + 2, 0)
        pattern = r"Преподаватель (\w+) (\w\.\w\.)"
        match = re.search(pattern, teacher_name_row)
        if match:
            return f"{match.group(1)} {match.group(2)}"
        else:
            return "Unknown"

    def _cut_cabinet(self, sheet, row, column):
        discipline_data = sheet.cell_value(row, column + 1)
        discipline_data = ' '.join(discipline_data.split())
        pattern = r'\(.*?(\d{2,3}).*?\)'
        match = re.search(pattern, discipline_data)
        cabinet_number = match.group(1) if match else None
        cabinet = f"К3-{cabinet_number}"
        return cabinet

    def _cut_group(self, sheet, row, column):
        discipline_data = sheet.cell_value(row, column + 1)
        discipline_data = ' '.join(discipline_data.split())
        group_pattern = r'(МД-\d{2}-о)'
        match = re.search(group_pattern, discipline_data)
        group_name = match.group(1) if match else None
        return group_name

    def _cut_student_name(self, sheet, row, column):
        student_name_cell = sheet.cell_value(row, column)
        student_name_cell = ' '.join(student_name_cell.split())

        # Проверяем наличие символа '/'
        if '/' in student_name_cell:
            # Разделяем по символу '/' и убираем лишние пробелы
            student_names = [name.strip() for name in student_name_cell.split('/')]
            # Если после слеша нет ничего, заполняем None
            student_names = [name if name else None for name in student_names]
        else:
            # Если слеша нет, создаем список из двух одинаковых имен
            student_names = [student_name_cell, student_name_cell]

        return student_names

    def _get_days_columns(self, sheet, teacher_table_row):
        days_columns = []
        days_header_row = teacher_table_row + 5
        for day in range(2, sheet.ncols, 3):
            day_name = sheet.cell_value(days_header_row, day)
            if day_name == "":
                break
            days_columns.append(day)
        return days_columns

    def _load_file_paths(self):
        directory = os.path.join(settings.DATA_DIRECTORY, "ind_sched")
        for filename in os.listdir(directory):
            if filename.endswith('.xls'):  # Проверяем, что файл имеет нужное расширение
                self.file_paths.append(os.path.join(directory, filename))


if __name__ == "__main__":
    parser = RequestsScheduleParser(
        department_name="Факультет искусств и физической культуры",
        group_name="МД-24-о",
    )
    group_lessons = parser.parse()
    for lesson in group_lessons:
        print(lesson.discipline)


