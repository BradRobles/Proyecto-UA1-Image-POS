import time
import os
import pandas as pd
from datetime import datetime

# Catálogo Duro
CATALOGO = {
    "Pollo": {"price": 5.50},
    "Tortuga": {"price": 12.00},
    "Cohete": {"price": 25.00},
    "Cartas pokemon": {"price": 4.99},
    "Sylveon": {"price": 15.00}
}

DB_PATH = "base_datos/ventas.csv"

class POSLogic:
    def __init__(self):
        self.current_ticket = []
        
        # State machine for 1.5s detection
        self.tracking_label = None
        self.tracking_start_time = None
        self.confidence_threshold = 0.85
        self.time_threshold = 1.5
        
        # Ensure DB directory and file exist
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        if not os.path.exists(DB_PATH):
            df = pd.DataFrame(columns=["Timestamp", "TicketID", "ProductName", "Price", "ScanSource"])
            df.to_csv(DB_PATH, index=False)

    def process_vision_signal(self, label, confidence):
        """
        Receives AI signal. Emits product dict to add if logic is met, else None.
        """
        if label == "Unknown" or label not in CATALOGO:
            self.tracking_label = None
            self.tracking_start_time = None
            return None
            
        if confidence >= self.confidence_threshold:
            if self.tracking_label == label:
                # Same label, check duration
                elapsed = time.time() - self.tracking_start_time
                if elapsed >= self.time_threshold:
                    # Item successfully scanned
                    # Reset state machine to prevent multiple scans of the same item instantly
                    self.tracking_label = None
                    self.tracking_start_time = None
                    return self.add_item_to_ticket(label, source="Visión IA")
            else:
                # New label with high confidence, start tracking
                self.tracking_label = label
                self.tracking_start_time = time.time()
        else:
            # Lost confidence
            self.tracking_label = None
            self.tracking_start_time = None
            
        return None

    def add_item_to_ticket(self, label, source="Botón Manual"):
        if label in CATALOGO:
            item = {
                "name": label,
                "price": CATALOGO[label]["price"],
                "source": source
            }
            self.current_ticket.append(item)
            return item
        return None

    def get_current_ticket(self):
        return self.current_ticket
        
    def get_ticket_total(self):
        return sum(item["price"] for item in self.current_ticket)
        
    def clear_ticket(self):
        self.current_ticket = []
        
    def remove_item(self, index):
        if 0 <= index < len(self.current_ticket):
            self.current_ticket.pop(index)

    def checkout(self):
        if not self.current_ticket:
            return False
            
        ticket_id = int(time.time())
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        records = []
        for item in self.current_ticket:
            records.append({
                "Timestamp": now_str,
                "TicketID": ticket_id,
                "ProductName": item["name"],
                "Price": item["price"],
                "ScanSource": item["source"]
            })
            
        df = pd.DataFrame(records)
        df.to_csv(DB_PATH, mode='a', header=False, index=False)
        self.clear_ticket()
        return True
