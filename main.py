import sqlite3
from datetime import datetime


class Inventory:
    def __init__(self):
        self.items = {
            "milk": 4,
            "sausage": 5,
            "rice": 6,
            "beef": 10,
        }

    def display_items(self):
        print("Available items:")
        for item, price in self.items.items():
            print(f"- {item}: ${price}")

    def is_valid_item(self, item_name):
        return item_name.lower() in self.items

    def get_price(self, item_name):
        return self.items[item_name.lower()]


class SalesDatabase:
    def __init__(self, database_name="sales.db"):
        self.conn = sqlite3.connect(database_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                item TEXT,
                quantity INTEGER,
                unit_price REAL,
                subtotal REAL
            )
            '''
        )
        self.conn.commit()

    def save_sale(self, item, quantity, unit_price, subtotal):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            '''
            INSERT INTO sales (date, item, quantity, unit_price, subtotal)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (current_time, item, quantity, unit_price, subtotal),
        )
        self.conn.commit()

    def show_history(self):
        self.cursor.execute("SELECT * FROM sales ORDER BY id DESC LIMIT 10")
        rows = self.cursor.fetchall()

        if not rows:
            print("No sales history yet.")
            return

        print("\nSales history:")
        print(f"{'ID':<5} {'Date':<20} {'Item':<12} {'Qty':<5} {'Unit Price':<12} {'Subtotal':<12}")
        print("-" * 75)

        for row in rows:
            sale_id, date, item, quantity, unit_price, subtotal = row
            print(f"{sale_id:<5} {date:<20} {item:<12} {quantity:<5} ${unit_price:<11.2f} ${subtotal:<11.2f}")

    def get_daily_revenue(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute(
            "SELECT SUM(subtotal) FROM sales WHERE date LIKE ?",
            (today + "%",),
        )
        result = self.cursor.fetchone()[0]
        revenue = result if result is not None else 0
        print(f"\nToday's revenue: ${revenue:.2f}")

    def close(self):
        self.conn.close()


class POSSystem:
    def __init__(self):
        self.inventory = Inventory()
        self.database = SalesDatabase()

    def parse_input(self, buyer_input):
        entries = []
        raw_items = buyer_input.split(",")

        for raw_item in raw_items:
            clean_item = raw_item.strip()
            if not clean_item:
                continue

            parts = clean_item.split()
            if len(parts) != 2:
                raise ValueError(f"Invalid format: '{clean_item}'. Use: 'milk 2'")

            item_name, quantity_text = parts
            item_name = item_name.lower()

            if not self.inventory.is_valid_item(item_name):
                raise ValueError(f"Item '{item_name}' is not in the inventory.")

            try:
                quantity = int(quantity_text)
            except ValueError:
                raise ValueError(f"Quantity '{quantity_text}' is not valid.")

            if quantity <= 0:
                raise ValueError(f"Quantity must be greater than zero.")

            entries.append((item_name, quantity))

        return entries

    def calculate_receipt(self, items):
        total_price = 0
        receipt = []

        print("\nReceipt")
        print("-" * 40)
        print(f"{'Item':<12} {'Qty':<5} {'Price':<10} {'Subtotal':<12}")
        print("-" * 40)

        for item_name, quantity in items:
            unit_price = self.inventory.get_price(item_name)
            subtotal = unit_price * quantity
            total_price += subtotal

            self.database.save_sale(item_name, quantity, unit_price, subtotal)
            receipt.append((item_name, quantity, unit_price, subtotal))

            print(f"{item_name:<12} {quantity:<5} ${unit_price:<9.2f} ${subtotal:<11.2f}")

        print("-" * 40)
        print(f"{'TOTAL':<28} ${total_price:>11.2f}")
        print("-" * 40)
        return total_price, receipt

    def show_menu(self):
        print("\nMini Market POS")
        print("1. Buy items")
        print("2. View sales history")
        print("3. View today's revenue")
        print("4. Exit")

    def run(self):
        while True:
            self.show_menu()
            choice = input("Choose an option: ").strip()

            if choice == "1":
                print("\nExample format: milk 2, sausage 1, rice 3")
                buyer_input = input("Buy items: ")

                try:
                    items = self.parse_input(buyer_input)
                    self.calculate_receipt(items)
                except ValueError as error:
                    print(f"Error: {error}")

            elif choice == "2":
                self.database.show_history()

            elif choice == "3":
                self.database.get_daily_revenue()

            elif choice == "4":
                print("Thank you for shopping!")
                self.database.close()
                break

            else:
                print("Invalid option. Please select 1, 2, 3 or 4.")


if __name__ == "__main__":
    pos = POSSystem()
    pos.inventory.display_items()
    pos.run()
