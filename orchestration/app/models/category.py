from app.extensions import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_deleted = db.Column(db.Boolean, default=False)

    tickets = db.relationship('Ticket', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'
