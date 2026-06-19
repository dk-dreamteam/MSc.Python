import os
import requests

API_URL = "http://localhost:5680"
PHOTOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "init_photos")

TICKETS = [
    {
        "filename": "amea.jpg",
        "title": "Πρόβλημα πρόσβασης ΑμεΑ",
        "description": "Η ράμπα για άτομα με αναπηρία επί της οδού Νοταρά έχει υποστεί ζημιές και χρειάζεται άμεση επισκευή.",
        "category_id": 7,
        "address": "Νοταρά 25, Πειραιάς",
    },
    {
        "filename": "tree.jpg",
        "title": "Κλαδιά δέντρου που χρειάζονται κλάδεμα",
        "description": "Μεγάλο δέντρο στην οδό Γρηγορίου Λαμπράκη έχει ξερά κλαδιά που κινδυνεύουν να πέσουν σε περαστικούς.",
        "category_id": 5,
        "address": "Γρηγορίου Λαμπράκη 45, Πειραιάς",
    },
    {
        "filename": "burnt_car.jpg",
        "title": "Εγκαταλελειμμένο καμένο όχημα",
        "description": "Ένα όχημα έχει εγκαταλειφθεί και καεί στην οδό Καραολή και Δημητρίου, μπροστά από την πλατεία.",
        "category_id": 6,
        "address": "Καραολή και Δημητρίου 12, Πειραιάς",
    },
    {
        "filename": "road_works.jpg",
        "title": "Λακκούβα στο οδόστρωμα",
        "description": "Μεγάλη λακκούβα στο οδόστρωμα της οδού Αθηνών, στο ύψος του Δημοτικού Θεάτρου, που προκαλεί κίνδυνο για οχήματα.",
        "category_id": 1,
        "address": "Αθηνών 70, Πειραιάς",
    },
    {
        "filename": "sidewalk.jpg",
        "title": "Κατεστραμμένο πεζοδρόμιο",
        "description": "Το πεζοδρόμιο επί της Ακτής Μιαούλη είναι ανάγκη να επισκευαστεί.",
        "category_id": 1,
        "address": "Ακτή Μιαούλη 10, Πειραιάς",
    },
    {
        "filename": "flood.jpg",
        "title": "Πλημμύρα λόγω βουλωμένου φρεατίου",
        "description": "Το φρεάτιο στην οδό Τζαβέλα έχει βουλώσει και τα νερά λιμνάζουν, δημιουργώντας προβλήματα στην κυκλοφορία.",
        "category_id": 4,
        "address": "Τζαβέλα 8, Πειραιάς",
    },
    {
        "filename": "electricity.jpg",
        "title": "Βλάβη σε κολώνα φωτισμού",
        "description": "Η κολώνα φωτισμού επί της οδού Βασιλέως Γεωργίου έχει υποστεί ζημιά και δεν λειτουργεί.",
        "category_id": 2,
        "address": "Βασιλέως Γεωργίου 15, Πειραιάς",
    },
]

for i, ticket in enumerate(TICKETS, 1):
    photo_path = os.path.join(PHOTOS_DIR, ticket["filename"])

    if not os.path.exists(photo_path):
        print(f"Ticket {i}: {ticket['filename']} not found, skipping.")
        continue

    with open(photo_path, "rb") as f:
        files = {"photo": (ticket["filename"], f, "image/jpeg")}
        data = {k: v for k, v in ticket.items() if k != "filename"}
        resp = requests.post(f"{API_URL}/tickets", data=data, files=files)

    if resp.ok:
        print(f"Ticket {i} created: {ticket['title']}")
    else:
        error = resp.json().get("error", resp.text)
        print(f"Ticket {i} failed: {error}")
