import os
import requests


class NotificationService:
    def __init__(self):
        self.topic = os.environ.get('NTFY_TOPIC', 'cityreport-notifications')
        self.base_url = os.environ.get('NTFY_URL', 'https://ntfy.sh')

    def send_notification(self, title, message, priority=3, tags=None):
        try:
            url = f'{self.base_url}/{self.topic}'
            headers = {
                'Title': title,
                'Priority': str(priority),
                'Tags': ','.join(tags) if tags else ''
            }
            requests.post(url, data=message.encode('utf-8'), headers=headers, timeout=5)
        except requests.RequestException:
            pass

    def notify_status_change(self, ticket_id, new_status, ticket_title):
        self.send_notification(
            title=f'Ticket {ticket_id}',
            message=f'Status changed to: {new_status}\n{ticket_title}',
            tags=['cityreport', 'status_update']
        )
