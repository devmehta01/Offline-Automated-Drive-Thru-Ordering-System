import re
import json
import os

class OrderSession:
    def __init__(self):
        self.items = []
        menu_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'menu.json')
        with open(menu_path, 'r') as f:
            self.menu = json.load(f)

    def add_items(self, new_items):
        for item in new_items:
            # Check if item with same name already exists
            for existing_item in self.items:
                if existing_item["name"].lower() == item["name"].lower():
                    existing_item["quantity"] += item.get("quantity", 1)
                    if "instructions" in item:
                        existing_item.setdefault("instructions", []).extend(item["instructions"])
                    break
            else:
                self.items.append(item)

    def is_order_complete(self, transcript):
        complete_phrases = [
            r"that's all", r"that'll be all", r"i'm done", r"confirm order", r"that is it", r"done"
        ]
        transcript = transcript.lower()
        return any(re.search(phrase, transcript) for phrase in complete_phrases)

    def summarize_order(self):
        summary = []
        for item in self.items:
            line = f"{item['quantity']} x {item['name']}"
            if "instructions" in item and item["instructions"]:
                line += f" ({', '.join(item['instructions'])})"
            summary.append(line)
        return "\n".join(summary)
    
    def update_item(self, update_data):
        """
        update_data = {
            "action": "modify" / "remove",
            "name": "Veggie Burger",
            "instructions": ["no onions"],
            "quantity": 2  # optional
        }
        """
        for item in self.items:
            if item["name"].lower() == update_data["name"].lower():
                if update_data.get("action") == "remove":
                    self.items.remove(item)
                    return
                if update_data.get("instructions"):
                    item.setdefault("instructions", []).extend(update_data["instructions"])
                if update_data.get("quantity"):
                    item["quantity"] = update_data["quantity"]
                return
    def get_current_order_json(self):
        return json.dumps({"order": self.items}, indent=2)
    
    def update_from_llm(self, parsed_response):
        if "order" not in parsed_response:
            return

        for update in parsed_response["order"]:
            item = update.get("item")
            qty = update.get("quantity", 1)
            instructions = update.get("instructions", [])
            action = update.get("action")

            if not item or not action:
                continue

            # Normalize item name
            item = item.lower()

            if action == "add":
                self.items.append({
                    "item": item,
                    "quantity": qty,
                    "instructions": instructions
                })

            elif action == "modify":
                found = False
                for entry in self.items:
                    if entry["item"] == item:
                        entry["quantity"] = qty
                        entry["instructions"] = instructions
                        found = True
                        break
                if not found:
                    # If item doesn't exist yet, treat as an add
                    self.items.append({
                        "item": item,
                        "quantity": qty,
                        "instructions": instructions
                    })

            elif action == "remove":
                self.items = [entry for entry in self.items if entry["item"] != item]
    
    def get_current_order_pretty(self):
        if not self.items:
            return "No items in the order."

        lines = []
        total = 0.0

        for entry in self.items:
            name = entry["item"]
            qty = entry["quantity"]
            instr = entry.get("instructions", [])
            instr_str = f" (Instructions: {', '.join(instr)})" if instr else ""

            # Look up price
            price = self._get_price(name)
            line_total = price * qty
            total += line_total

            lines.append(f"- {qty} × {name.capitalize()}{instr_str} — ${line_total:.2f}")

        lines.append(f"\nTotal: ${total:.2f}")
        return "\n".join(lines)

    def _get_price(self, item_name):
        for section_items in self.menu.values():
            for entry in section_items:
                if entry["name"].lower() == item_name.lower():
                    return entry["price"]
        return 0.0  # fallback if not found