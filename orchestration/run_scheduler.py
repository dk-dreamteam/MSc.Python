import time
import schedule
from app import create_app
from app.extensions import db
from app.models.ticket import Ticket
from app.models.status import Status
from app.services.ai_service import AIService
from app.services.notification_service import NotificationService

app = create_app()
ai_service = AIService()
notification_service = NotificationService()


def process_unanalyzed_tickets():
    with app.app_context():
        tickets = Ticket.query.filter(
            Ticket.ai_priority_suggestion.is_(None),
            Ticket.is_deleted == False
        ).all()

        for ticket in tickets:
            result = ai_service.analyze_ticket(ticket.title, ticket.description)
            ticket.ai_priority_suggestion = result['priority']
            ticket.ai_category_confidence = result['confidence']
            db.session.commit()


def send_daily_summary():
    with app.app_context():
        total = Ticket.query.filter_by(is_deleted=False).count()
        open_count = Ticket.query.join(Status).filter(
            Status.name.notin_(['Επιλύθηκε', 'Απορρίφθηκε']),
            Ticket.is_deleted == False
        ).count()

        notification_service.send_notification(
            title='CityReport Καθημερινή Σύνοψη',
            message=f'Σύνολο αναφορών: {total}\nΑνοιχτές: {open_count}',
            tags=['cityreport', 'daily_summary']
        )


schedule.every(10).minutes.do(process_unanalyzed_tickets)
schedule.every().day.at('09:00').do(send_daily_summary)

if __name__ == '__main__':
    print('Scheduler started...')
    while True:
        schedule.run_pending()
        time.sleep(60)
