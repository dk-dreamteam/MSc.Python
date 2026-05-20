from flask import request, jsonify
from marshmallow import ValidationError
from app.extensions import db
from app.models.ticket import Ticket
from app.models.category import Category
from app.models.status import Status
from app.schemas.ticket_schema import (
    TicketSchema, TicketCreateSchema, TicketUpdateSchema,
    CategorySchema, StatusSchema
)
from app.services.ai_service import AIService
from app.services.photo_service import PhotoService
from app.services.notification_service import NotificationService
from app.services.geocoding_service import GeocodingService
from app.api.cityReportApi import city_report_bp

ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)
category_schema = CategorySchema(many=True)
status_schema = StatusSchema(many=True)
create_schema = TicketCreateSchema()
update_schema = TicketUpdateSchema()

ai_service = AIService()
photo_service = PhotoService()
notification_service = NotificationService()
geocoding_service = GeocodingService()


@city_report_bp.route('/tickets', methods=['POST'])
def create_ticket():
    json_data = request.get_json(silent=True)
    file = request.files.get('photo')

    if json_data:
        try:
            data = create_schema.load(json_data)
        except ValidationError as err:
            return jsonify({'errors': err.messages}), 400
    elif request.form:
        try:
            data = create_schema.load(request.form.to_dict())
        except ValidationError as err:
            return jsonify({'errors': err.messages}), 400
    else:
        return jsonify({'error': 'No input data provided'}), 400

    address = geocoding_service.reverse_geocode(
        data['latitude'], data['longitude']
    )

    ai_result = ai_service.analyze_ticket(
        data.get('title', ''), data.get('description', '')
    )

    default_status = Status.query.filter_by(name='Δημιουργήθηκε').first()
    if not default_status:
        default_status = Status.query.first()

    ticket = Ticket(
        title=data.get('title'),
        description=data.get('description'),
        category_id=data.get('category_id'),
        status_id=default_status.id if default_status else None,
        latitude=data['latitude'],
        longitude=data['longitude'],
        address=address,
        ai_priority_suggestion=ai_result['priority'],
        ai_category_confidence=ai_result['confidence']
    )

    if file:
        photo_url = photo_service.upload_photo(file.read(), file.filename)
        ticket.photo_url = photo_url

    db.session.add(ticket)
    db.session.commit()

    return jsonify({
        'message': 'Ticket created successfully',
        'ticket': ticket_schema.dump(ticket)
    }), 201


@city_report_bp.route('/tickets/<uuid:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    ticket = Ticket.query.filter_by(id=ticket_id, is_deleted=False).first()
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    return jsonify({'ticket': ticket_schema.dump(ticket)})


@city_report_bp.route('/tickets/<uuid:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    ticket = Ticket.query.filter_by(id=ticket_id, is_deleted=False).first()
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        data = update_schema.load(json_data, partial=True)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    for field in ('title', 'description'):
        if field in data:
            setattr(ticket, field, data[field])

    file = request.files.get('photo')
    if file:
        if ticket.photo_url:
            photo_service.delete_photo(ticket.photo_url)
        photo_url = photo_service.upload_photo(file.read(), file.filename)
        ticket.photo_url = photo_url

    db.session.commit()
    return jsonify({
        'message': 'Ticket updated successfully',
        'ticket': ticket_schema.dump(ticket)
    })


@city_report_bp.route('/tickets', methods=['GET'])
def list_tickets():
    query = Ticket.query.filter_by(is_deleted=False)

    category_id = request.args.get('category_id', type=int)
    if category_id:
        query = query.filter_by(category_id=category_id)

    status_id = request.args.get('status_id', type=int)
    if status_id:
        query = query.filter_by(status_id=status_id)

    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')

    sort_column = getattr(Ticket, sort_by, Ticket.created_at)
    if sort_order == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'tickets': tickets_schema.dump(pagination.items),
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages
    })


@city_report_bp.route('/tickets/<uuid:ticket_id>/status', methods=['PUT'])
def update_ticket_status(ticket_id):
    ticket = Ticket.query.filter_by(id=ticket_id, is_deleted=False).first()
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    json_data = request.get_json(silent=True)
    if not json_data or 'status_id' not in json_data:
        return jsonify({'error': 'status_id is required'}), 400

    status = Status.query.get(json_data['status_id'])
    if not status:
        return jsonify({'error': 'Status not found'}), 404

    ticket.status_id = status.id
    ticket.admin_notes = json_data.get('admin_notes', ticket.admin_notes)
    db.session.commit()

    notification_service.notify_status_change(
        str(ticket.id), status.name, ticket.title
    )

    return jsonify({
        'message': 'Status updated successfully',
        'ticket': ticket_schema.dump(ticket)
    })


@city_report_bp.route('/tickets/<uuid:ticket_id>/notes', methods=['PUT'])
def update_ticket_notes(ticket_id):
    ticket = Ticket.query.filter_by(id=ticket_id, is_deleted=False).first()
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    json_data = request.get_json(silent=True)
    if not json_data or 'admin_notes' not in json_data:
        return jsonify({'error': 'admin_notes is required'}), 400

    ticket.admin_notes = json_data['admin_notes']
    db.session.commit()

    return jsonify({
        'message': 'Notes updated successfully',
        'ticket': ticket_schema.dump(ticket)
    })


@city_report_bp.route('/statuses', methods=['GET'])
def list_statuses():
    statuses = Status.query.filter_by(is_deleted=False).all()
    return jsonify({'statuses': status_schema.dump(statuses)})


@city_report_bp.route('/categories', methods=['GET'])
def list_categories():
    categories = Category.query.filter_by(is_deleted=False).all()
    return jsonify({'categories': category_schema.dump(categories)})


@city_report_bp.route('/stats', methods=['GET'])
def get_statistics():
    total_tickets = Ticket.query.filter_by(is_deleted=False).count()
    by_status = db.session.query(
        Status.name, db.func.count(Ticket.id)
    ).join(Status, Ticket.status_id == Status.id
    ).filter(Ticket.is_deleted == False
    ).group_by(Status.name).all()

    by_category = db.session.query(
        Category.name, db.func.count(Ticket.id)
    ).join(Category, Ticket.category_id == Category.id
    ).filter(Ticket.is_deleted == False
    ).group_by(Category.name).all()

    return jsonify({
        'total_tickets': total_tickets,
        'by_status': dict(by_status),
        'by_category': dict(by_category)
    })
