import imaplib
import email
from email.header import decode_header
import os
from datetime import datetime, timedelta

from config import settings


class EmailScheduleManager:
    """
    Этот класс отвечает за получение таблиц с расписанием индивидуальных занятий
    через электронную почту. Удаляет залежавшиеся письма, скачивает новое
    расписание.
    """

    def __init__(self):
        self.imap_server = settings.IMAP_SERVER
        self.email_address = settings.EMAIL_ADDRESS
        self.email_password = settings.EMAIL_PASSWORD

        self.save_folder = os.path.join(settings.DATA_DIRECTORY, "ind_sched")
        self.days_before_delete = 28
        self.mail = None

    def process_letters(self):
        self._connect_to_mail()
        self._delete_old_letters()
        letter_indexes = self._get_all_letters()
        for index in letter_indexes:
            # Используем uid для получения письма
            status, data = self.mail.uid('fetch', index, "(RFC822)")

            # Проверка успешности выполнения fetch и того, что data не None
            if status != 'OK' or data is None or len(data) < 2:
                print(f"Ошибка при получении письма с индексом {index}: {status}")
                continue  # Переходим к следующему индексу

            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Если письмо мультипарт
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue

                    filename = part.get_filename()
                    decoded = decode_header(filename)[0]
                    filename = decoded[0].decode(decoded[1] or 'utf-8') if isinstance(decoded[0], bytes) else decoded[0]

                    if filename and filename.lower().endswith('.xls'):
                        # Декодируем имя файла с учетом кириллицы

                        # Сохраняем файл
                        filepath = os.path.join(self.save_folder, filename)
                        with open(filepath, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                        print(f"Сохранен файл: {filename}")

        self.mail.logout()

    def _connect_to_mail(self):
        mail = imaplib.IMAP4_SSL(self.imap_server)
        mail.login(self.email_address, self.email_password)
        mail.select("INBOX")
        self.mail = mail

    def _delete_old_letters(self):
        cutoff_date = (datetime.now() - timedelta(days=self.days_before_delete)).strftime("%d-%b-%Y")
        status, data = self.mail.search(None, 'BEFORE', cutoff_date)
        if status != 'OK':
            print("Ошибка поиска писем")
            self.mail.close()
            self.mail.logout()
            return

        email_ids = data[0].split()
        print(f"Найдено писем для удаления: {len(email_ids)}")

        # Проходим по найденному списку и отмечаем каждое письмо для удаления
        for eid in email_ids:
            status, _ = self.mail.store(eid, '+FLAGS', '\\Deleted')
            if status == 'OK':
                print(f"Письмо {eid.decode('utf-8')} успешно помечено для удаления")
            else:
                print(f"Ошибка при пометке письма {eid.decode('utf-8')} для удаления")

        self.mail.expunge()

    def _get_all_letters(self):
        status_code, bytes_letter_indexes = self.mail.uid('search', "ALL")
        indexes_str = bytes_letter_indexes[0].decode("utf-8").split()
        return indexes_str


if __name__ == "__main__":
    manager = EmailScheduleManager()
    manager.process_letters()
