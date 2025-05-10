def main(*args,**kwargs):
    """
    Main function to run the application.
    """
    print("Running the main application...")

# Check if the script is being run directly
if __name__ == "__main__":
    # Call the run_app function from the app module
    main()
else:
    # If not, print a message indicating that the script is not being run directly
    print("This script is not being run directly.")