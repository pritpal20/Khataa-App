from sales_data import BillCalculator


def main():
    
    """
    Main function to run the application.
    """
    print("Running the main application...")

    # Example usage
    price_file = "data.csv"
    input_file = "input_data.csv"
    calculator = BillCalculator(price_file, input_file)
    total = calculator.calculate_bill()
    print(f"Total Bill: ${total}")
    calculator.generate_bill()
    calculator.write_bill_to_pdf("bill.pdf")



if __name__ == "__main__":
    main()
