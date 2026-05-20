from app.extensions import db


class Status(db.Model):
    __tablename__ = 'statuses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_deleted = db.Column(db.Boolean, default=False)

    tickets = db.relationship('Ticket', backref='status', lazy='dynamic')

    def __repr__(self):
        return f'<Status {self.name}>'
