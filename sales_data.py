import csv
from fpdf import FPDF
import json

class BillCalculator:
    def __init__(self, price_file, input_file):
        self.price_file = price_file
        self.input_file = input_file
        self.prices = self.load_prices()

    def load_prices(self):
        prices = {}
        try:
            with open(self.price_file, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    item = row['item']
                    price = float(row['price'])
                    prices[item] = price
        except FileNotFoundError:
            print(f"Error: {self.price_file} not found.")
        except KeyError:
            print("Error: Invalid format in price file.")
        return prices

    def calculate_bill(self):
        sales_data = {}
        try:
            with open(self.input_file, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    item = row['item']
                    quantity = float(row['quantity'])
                    client_name = row['client']
                    units = row['units']
                    
                    if item in self.prices:
                        if client_name not in sales_data:
                            sales_data[client_name] = {}
                        if item not in sales_data[client_name]:
                            sales_data[client_name][item] = {
                                'quantity': 0,
                                'total_price': 0
                            }
                        sales_data[client_name][item]['quantity'] += quantity
                        sales_data[client_name][item]['price'] = self.prices[item]
                        sales_data[client_name][item]['total_price'] += self.prices[item] * quantity
                        sales_data[client_name][item]['units'] = units
                    else:
                        print(f"Warning: Price for item '{item}' not found.")
        except FileNotFoundError:
            print(f"Error: {self.input_file} not found.")
        except KeyError:
            print("Error: Invalid format in input file.")
        return sales_data
    
    def generate_bill(self):
        sales_data = self.calculate_bill()
        total_bill = 0
        for client, items in sales_data.items():
            for item, details in items.items():
                total_bill += details['total_price']
        return sales_data
    
    def add_invoice_header(self, pdf):
        # Load settings from a JSON file
        try:
            with open("invoice_settings.json", "r") as file:
                settings = json.load(file)
        except FileNotFoundError:
            print("Error: invoice_settings.json not found.")
            return
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in invoice_settings.json.")
            return

        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Use settings from the JSON file
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(200, 10, txt=settings["company_details"].get("name",""), ln=True, align='L')
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 9, txt=settings["company_details"].get("address", ""), ln=True, align='L')
        pdf.cell(200, 9, txt=settings["company_details"].get("phone", ""), align='L', ln=True)
        pdf.cell(200, 9, txt=settings["company_details"].get("email", ""), ln=True, align='L')
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(200, 2, txt=settings.get("separator", ""), ln=True, align='left', fill=True)
        pdf.cell(200, 10, txt=settings.get("invoice_title", ""), align='C', ln=True)
        pdf.ln(10)

    
    def write_bill_to_pdf(self, output_file, sales_data=None):

        if sales_data is None:
            # If sales_data is not provided, calculate it
            sales_data = self.calculate_bill()
        # If sales_data is provided, use it directly
        # Create a PDF object
        pdf = FPDF()
        self.add_invoice_header(pdf)
        
        total_bill = 0
        for client, items in sales_data.items():

            pdf.set_font("Arial", style='B', size=12)
            pdf.cell(200, 10, txt=f"Bill to   :    {client}", ln=True)
            pdf.set_font("Arial", size=12)
            count = 0
            # Add a header for the items table
            pdf.set_font("Arial", style='B', size=12)
            pdf.cell(14, 10, txt="S.No", border=1, align='C')
            pdf.cell(50, 10, txt="Item", border=1, align='C')
            pdf.cell(40, 10, txt="Quantity", border=1, align='C')
            pdf.cell(15, 10, txt="Units", border=1, align='C')
            pdf.cell(40, 10, txt="Price/unit", border=1, align='C')
            pdf.cell(40, 10, txt="Total Price", border=1, align='C')
            pdf.ln(10)
            
            for item, details in items.items():
                count+=1
                pdf.set_font("Arial", size=12)
                pdf.cell(14, 10, txt=str(count), border=1, align='C')
                pdf.cell(50, 10, txt=item, border=1, align='C')
                pdf.cell(40, 10, txt=str(details['quantity']), border=1, align='C')
                pdf.cell(15, 10, txt=str(details['units']), border=1, align='C')
                pdf.cell(40, 10, txt=str(details['price']), border=1, align='C')
                pdf.cell(40, 10, txt=f"Rs {details['total_price']:.2f}", border=1, align='C')
                pdf.ln(10)
                total_bill += details['total_price']
            pdf.ln(5)

        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(0, 10, txt=f"Total amount: Rs {total_bill:.2f}", ln=True,align='R')

        try:
            pdf.output(output_file)
            print(f"Bill successfully written to {output_file}")
        except Exception as e:
            print(f"Error writing to PDF: {e}")

# Example usage
if __name__ == "__main__":
    price_file = "data.csv"
    input_file = "input_data.csv"
    calculator = BillCalculator(price_file, input_file)
    data = calculator.generate_bill()

    print(data)
    print("*******************")
    count = 1
    for client,items in data.items():
        print(f"Client: {client}")
        print(f"Items: {items}")
        client_data = {}
        client_data[client] = items
        calculator.write_bill_to_pdf(f"bill_{count}.pdf",client_data)
        count += 1
