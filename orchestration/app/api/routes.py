import io
import json
import mimetypes
import os
from flask import Flask, request, send_file
from flasgger import Swagger
from data.repository import TicketRepository
from photo_blob_service import PhotoBlobService
from queue_sender_service import QueueSenderService

city_report_api = Flask(__name__)
Swagger(city_report_api, template={
    "swagger": "2.0",
    "info": {
        "title": "CityReport API",
        "description": "API for CityReport citizen issue reporting system",
        "version": "1.0.0",
    },
    "definitions": {
        "Ticket": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "category_id": {"type": "integer"},
                "status_id": {"type": "integer"},
                "latitude": {"type": "number", "format": "float"},
                "longitude": {"type": "number", "format": "float"},
                "address": {"type": "string"},
                "photo_url": {"type": "string"},
                "ai_priority_suggestion": {"type": "string"},
                "ai_category_confidence": {"type": "number", "format": "float"},
                "admin_notes": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"},
                "status_name": {"type": "string"},
                "category_name": {"type": "string"},
            },
        },
    },
})
repo = TicketRepository()
blob_service = PhotoBlobService()
queue_service = QueueSenderService()
port = int(os.getenv("APP_PORT"))

TOPIC_NAME = os.getenv("TOPIC_NAME")
if not TOPIC_NAME:
    raise ValueError("TOPIC_NAME must be set")

@city_report_api.route('/tickets', methods=['POST'])
def create_ticket():
    """
    Create a new ticket
    ---
    tags:
      - Tickets
    consumes:
      - application/json
      - multipart/form-data
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              description: Ticket title
            description:
              type: string
              description: Ticket description
            category_id:
              type: integer
              description: Category ID
            latitude:
              type: number
              format: float
              description: Latitude coordinate
            longitude:
              type: number
              format: float
              description: Longitude coordinate
            address:
              type: string
              description: Street address
            photo:
              type: file
              description: Photo file (multipart only)
    responses:
      201:
        description: Ticket created successfully
        schema:
          type: object
          properties:
            message:
              type: string
            ticket:
              $ref: '#/definitions/Ticket'
      400:
        description: Missing required fields
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal server error
    """
    if request.is_json:
        data = request.get_json()
        file = None
    else:
        data = request.form.to_dict()
        file = request.files.get("photo")

    if not data:
        return json.dumps({"error": "Request body is required"}), 400, {"Content-Type": "application/json"}

    required = ["title", "description"]
    missing = [f for f in required if f not in data]
    if missing:
        return json.dumps({"error": f"Missing required fields: {', '.join(missing)}"}), 400, {"Content-Type": "application/json"}

    try:
        blob_name = None
        status_id = 1  # Δημιουργήθηκε
        data["status_id"] = status_id
        if file and file.filename:
            blob_name = blob_service.upload(file.read(), file.filename)
            data["photo_url"] = blob_name
        ticket = repo.create_ticket(data)
        if blob_name:
            full_url = f"http://localhost:{port}/tickets/{ticket.id}/photo?blob={blob_name}"
            ticket = repo.update_ticket(str(ticket.id), {"photo_url": full_url})

        queue_service.send_for_preprocessing(id=ticket.id)

        queue_service.send_notification(
            topic_name=TOPIC_NAME,
            title=f"🚨 Νέο συμβάν: {ticket.title}",
            payload=f"Περιγραφή: '{ticket.description}'",
            click_url=f"http://localhost:5682/ticket_detail?ticket_id={ticket.id}",
        )

        return json.dumps({"message": "Ticket created successfully", "ticket": ticket.to_dict()}), 201, {"Content-Type": "application/json"}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}


@city_report_api.route('/tickets/<uuid:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """
    Get a ticket by ID
    ---
    tags:
      - Tickets
    parameters:
      - name: ticket_id
        in: path
        type: string
        format: uuid
        required: true
        description: UUID of the ticket
    responses:
      200:
        description: Ticket retrieved successfully
        schema:
          type: object
          properties:
            message:
              type: string
            ticket:
              $ref: '#/definitions/Ticket'
      404:
        description: Ticket not found
      500:
        description: Internal server error
    """
    try:
        ticket = repo.get_ticket(str(ticket_id))
        if not ticket:
            return json.dumps({"error": "Ticket not found"}), 404, {"Content-Type": "application/json"}
        return json.dumps({"message": "Ticket retrieved successfully", "ticket": ticket.to_dict()}), 200, {"Content-Type": "application/json"}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}


@city_report_api.route('/tickets/<uuid:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    """
    Update a ticket
    ---
    tags:
      - Tickets
    parameters:
      - name: ticket_id
        in: path
        type: string
        format: uuid
        required: true
        description: UUID of the ticket
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
            category_id:
              type: integer
            latitude:
              type: number
              format: float
            longitude:
              type: number
              format: float
            address:
              type: string
            photo_url:
              type: string
    responses:
      200:
        description: Ticket updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
            ticket:
              $ref: '#/definitions/Ticket'
      400:
        description: Request body is required
      404:
        description: Ticket not found
      500:
        description: Internal server error
    """
    data = request.get_json()
    if not data:
        return json.dumps({"error": "Request body is required"}), 400, {"Content-Type": "application/json"}
    try:
        ticket = repo.update_ticket(str(ticket_id), data)
        if not ticket:
            return json.dumps({"error": "Ticket not found"}), 404, {"Content-Type": "application/json"}
        return json.dumps({"message": "Ticket updated successfully", "ticket": ticket.to_dict()}), 200, {"Content-Type": "application/json"}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}


@city_report_api.route('/tickets', methods=['GET'])
def get_tickets():
    """
    List all tickets
    ---
    tags:
      - Tickets
    parameters:
      - name: status_id
        in: query
        type: integer
        required: false
        description: Filter by status ID
      - name: category_id
        in: query
        type: integer
        required: false
        description: Filter by category ID
    responses:
      200:
        description: Tickets listed successfully
        schema:
          type: object
          properties:
            message:
              type: string
            tickets:
              type: array
              items:
                $ref: '#/definitions/Ticket'
      500:
        description: Internal server error
    """
    status_id = request.args.get("status_id", type=int)
    category_id = request.args.get("category_id", type=int)
    try:
        tickets = repo.list_tickets(status_id=status_id, category_id=category_id)
        return json.dumps({"message": "Tickets listed successfully", "tickets": [t.to_dict() for t in tickets]}), 200, {"Content-Type": "application/json"}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}


@city_report_api.route('/tickets/<uuid:ticket_id>/status', methods=['PUT'])
def update_ticket_status(ticket_id):
    """
    Update ticket status
    ---
    tags:
      - Tickets
    parameters:
      - name: ticket_id
        in: path
        type: string
        format: uuid
        required: true
        description: UUID of the ticket
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            status_id:
              type: integer
              required: true
              description: New status ID
    responses:
      200:
        description: Ticket status updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
            ticket:
              $ref: '#/definitions/Ticket'
      400:
        description: status_id is required
      404:
        description: Ticket not found
      500:
        description: Internal server error
    """
    data = request.get_json()
    if not data or "status_id" not in data:
        return json.dumps({"error": "status_id is required"}), 400, {"Content-Type": "application/json"}
    try:
        ticket = repo.update_ticket_status(str(ticket_id), data["status_id"])
        if not ticket:
            return json.dumps({"error": "Ticket not found"}), 404, {"Content-Type": "application/json"}
        return json.dumps({"message": "Ticket status updated successfully", "ticket": ticket.to_dict()}), 200, {"Content-Type": "application/json"}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}


@city_report_api.route('/tickets/<uuid:ticket_id>/notes', methods=['PUT'])
def update_ticket_notes(ticket_id):
    """
    Update admin notes on a ticket
    ---
    tags:
      - Tickets
    parameters:
      - name: ticket_id
        in: path
        type: string
        format: uuid
        required: true
        description: UUID of the ticket
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            admin_notes:
              type: string
              required: true
              description: Admin notes
    responses:
      200:
        description: Ticket notes updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
            ticket:
              $ref: '#/definitions/Ticket'
      400:
        description: admin_notes is required
      404:
        description: Ticket not found
      500:
        description: Internal server error
    """
    data = request.get_json()
    if not data or "admin_notes" not in data:
        return json.dumps({"error": "admin_notes is required"}), 400, {"Content-Type": "application/json"}
    try:
        ticket = repo.update_ticket_notes(str(ticket_id), data["admin_notes"])
        if not ticket:
            return json.dumps({"error": "Ticket not found"}), 404, {"Content-Type": "application/json"}
        return json.dumps({"message": "Ticket notes updated successfully", "ticket": ticket.to_dict()}), 200, {"Content-Type": "application/json"}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}


@city_report_api.route('/tickets/<uuid:ticket_id>/photo', methods=['GET'])
def get_ticket_photo(ticket_id):
    """
    Download ticket photo
    ---
    tags:
      - Tickets
    parameters:
      - name: ticket_id
        in: path
        type: string
        format: uuid
        required: true
        description: UUID of the ticket
      - name: blob
        in: query
        type: string
        required: true
        description: Blob name of the photo
    responses:
      200:
        description: Photo file
        produces:
          - image/jpeg
          - image/png
      404:
        description: Photo not found
      500:
        description: Internal server error
    """
    try:
        blob_name = request.args.get("blob")
        if not blob_name:
            return json.dumps({"error": "Photo not found"}), 404, {"Content-Type": "application/json"}

        data = blob_service.download(blob_name)
        mime_type, _ = mimetypes.guess_type(blob_name)
        return send_file(io.BytesIO(data), mimetype=mime_type or "application/octet-stream")
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}


@city_report_api.route('/statuses', methods=['GET'])
def list_statuses():
    """
    List all statuses
    ---
    tags:
      - Statuses
    responses:
      200:
        description: Statuses listed successfully
        schema:
          type: object
          properties:
            message:
              type: string
            statuses:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  description:
                    type: string
    """
    statuses = [
        {"id": 1, "name": "Δημιουργήθηκε", "description": "Το πρόβλημα καταχωρήθηκε από τον πολίτη."},
        {"id": 2, "name": "Σε Εξέλιξη", "description": "Το πρόβλημα έχει ελεγχθεί και γίνονται ενέργειες επίλυσης."},
        {"id": 3, "name": "Επιλύθηκε", "description": "Το πρόβλημα έχει αντιμετωπιστεί επιτυχώς."},
        {"id": 4, "name": "Απορρίφθηκε", "description": "Η αναφορά δεν ευσταθεί ή δεν είναι εφικτή η επίλυση."},
    ]
    return json.dumps({"message": "Statuses listed successfully", "statuses": statuses}), 200, {"Content-Type": "application/json"}
