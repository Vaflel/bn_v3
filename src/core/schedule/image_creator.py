import os

from jinja2 import Template
import imgkit

from src.core.schedule.schemas import WeekSchedule


class ImageCreator:
    def __init__(self, schedule):
        self.schedule: WeekSchedule = schedule

    def generate_image(self):
        styles = '''
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap');

                body {
                    font-family: 'Open Sans', sans-serif;
                }

                table { 
                    border-collapse: collapse; 
                    width: 100%; 
                }
                th, td { 
                    border: 1px solid #96a8bb; 
                    padding: 10px; 
                    text-align: left; 
                }
                th { 
                    background-color: #f8f9fa; 
                }
                caption { 
                    font-size: 24px; 
                    margin: 10px; 
                }
                .table-container { 
                    border: 1px solid #96a8bb; 
                    margin-bottom: 20px; 
                }
                .table-header, .day-header { 
                    padding: 20px; 
                    margin: 20px; 
                    background-color: #3257C2; 
                    color: white; 
                }                
                .column-header th { 
                    background-color: #3257C2; 
                    color: white; 
                }
                .column-1 { width: 15%; }
                .column-2 { width: 40%; }
                .column-3 { width: 30%; }
                .column-4 { width: 15%; }
            </style>
        '''

        html_template = Template('''
        <html>
        <head>
            ''' + styles + '''
        </head>
        <body>
            <div class="table-container">
                <table>
                    <tr class="table-header">
                        <td colspan="4">{{ schedule.header }}</td>
                    </tr>
                    {% for day in schedule.days %}
                    <tr class="day-header">
                        <td colspan="4">{{ day.header }}</td>
                    </tr>
                    <tr class="column-header">
                        <th class="column-1">Время</th>
                        <th class="column-2">Дисциплина</th>
                        <th class="column-3">Преподаватель</th>
                        <th class="column-4">Аудитория</th>
                    </tr>
                    {% for pair in day.pairs %}
                    <tr>
                        <td class="column-1">
                            <div>{{ pair.time.number }} пара</div>
                            <div>{{ pair.time.start_time }} - {{ pair.time.end_time }}</div>
                        </td>
                        <td class="column-2">{{ pair.discipline }}</td>
                        <td class="column-3">{{ pair.teacher }}</td>
                        <td class="column-4">{{ pair.cabinet }}</td>
                    </tr>
                    {% endfor %}
                    {% endfor %}
                </table>
            </div>
        </body>
        </html>
        ''')

        # Генерация изображения
        options = {
            "format": "png",
            "width": 800,
            "encoding": "UTF-8"
        }

        #config = imgkit.config(wkhtmltoimage='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltoimage.exe')
        #config = imgkit.config(wkhtmltoimage='/usr/bin/wkhtmltoimage')

        # Определяем путь к wkhtmltoimage в зависимости от операционной системы
        if os.name == 'nt':  # Windows
            config = imgkit.config(wkhtmltoimage='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltoimage.exe')
        else:  # Linux и другие ОС
            config = imgkit.config(wkhtmltoimage='/usr/bin/wkhtmltoimage')

        # Теперь вы можете использовать config в вашем коде

        image_data = imgkit.from_string(
            html_template.render(schedule=self.schedule),
            False,  # Устанавливаем output_path в False
            options=options,
            config=config,
        )

        return image_data

        # imgkit.from_string(
        #     html_template.render(schedule=self.schedule),
        #     output_path=os.path.join(settings.DATA_DIRECTORY, f"{self.schedule.group_name} ({self.schedule.student}) schedule.png"),
        #     options=options,
        #     config=config,
        # )
