import io
import json
import mimetypes
import os
from flask import Flask, request, send_file
from orchestration.data.repository import TicketRepository
from photo_blob_service import PhotoBlobService

city_report_api = Flask(__name__)
repo = TicketRepository()
blob_service = PhotoBlobService()
port = int(os.getenv("APP_PORT"))


@city_report_api.route('/tickets', methods=['POST'])
def create_ticket():
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
        if file and file.filename:
            blob_name = blob_service.upload(file.read(), file.filename)
            data["photo_url"] = blob_name
        ticket = repo.create_ticket(data)
        if blob_name:
            full_url = f"http://localhost:{port}/tickets/{ticket.id}/photo?blob={blob_name}"
            ticket = repo.update_ticket(str(ticket.id), {"photo_url": full_url})
        return json.dumps({"message": "Ticket created successfully", "ticket": ticket.to_dict()}), 201, {"Content-Type": "application/json"}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}


@city_report_api.route('/tickets/<uuid:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    try:
        ticket = repo.get_ticket(str(ticket_id))
        if not ticket:
            return json.dumps({"error": "Ticket not found"}), 404, {"Content-Type": "application/json"}
        return json.dumps({"message": "Ticket retrieved successfully", "ticket": ticket.to_dict()}), 200, {"Content-Type": "application/json"}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}


@city_report_api.route('/tickets/<uuid:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
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
    status_id = request.args.get("status_id", type=int)
    category_id = request.args.get("category_id", type=int)
    try:
        tickets = repo.list_tickets(status_id=status_id, category_id=category_id)
        return json.dumps({"message": "Tickets listed successfully", "tickets": [t.to_dict() for t in tickets]}), 200, {"Content-Type": "application/json"}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"}


@city_report_api.route('/tickets/<uuid:ticket_id>/status', methods=['PUT'])
def update_ticket_status(ticket_id):
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
    statuses = [
        {"id": 1, "name": "Δημιουργήθηκε", "description": "Το πρόβλημα καταχωρήθηκε από τον πολίτη."},
        {"id": 2, "name": "Σε Εξέλιξη", "description": "Το πρόβλημα έχει ελεγχθεί και γίνονται ενέργειες επίλυσης."},
        {"id": 3, "name": "Επιλύθηκε", "description": "Το πρόβλημα έχει αντιμετωπιστεί επιτυχώς."},
        {"id": 4, "name": "Απορρίφθηκε", "description": "Η αναφορά δεν ευσταθεί ή δεν είναι εφικτή η επίλυση."},
    ]
    return json.dumps({"message": "Statuses listed successfully", "statuses": statuses}), 200, {"Content-Type": "application/json"}
