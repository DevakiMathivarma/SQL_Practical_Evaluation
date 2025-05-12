
import mysql.connector
from datetime import datetime

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2798",  # Replace with your MySQL password
    database="taxi_bookings"
)
cursor = db.cursor()

# Insert sample data into the database
def insert_sample_drivers():
    cursor.execute("""
        INSERT INTO drivers (name, phone_number, vehicle_model, license_number, availability)
        VALUES 
        ('John Doe', '1234567890', 'Toyota Corolla', 'XYZ123', TRUE),
        ('Jane Smith', '9876543210', 'Honda Civic', 'ABC456', TRUE);
    """)
    db.commit()

def insert_sample_customers():
    cursor.execute("""
        INSERT INTO customers (name, email, phone_number, address)
        VALUES 
        ('Alice Johnson', 'alice@example.com', '555-1234', '123 Elm St'),
        ('Bob Brown', 'bob@example.com', '555-5678', '456 Oak St');
    """)
    db.commit()

def insert_sample_bookings():
    cursor.execute("""
        INSERT INTO bookings (customer_id, driver_id, pickup_location, drop_location, distance, fare, booking_time)
        VALUES 
        (1, 1, '123 Elm St', '789 Maple Ave', 15, 35, NOW()),
        (2, 2, '456 Oak St', '123 Pine Rd', 20, 45, NOW());
    """)
    db.commit()

# Function to validate if input is a valid number
def validate_number_input(input_str, input_type=float):
    try:
        return input_type(input_str)
    except ValueError:
        print(f"Invalid input! Please enter a valid {input_type.__name__}.")
        return None

# Function to book a ride
def book_ride(customer_id, pickup_location, drop_location, distance):
    # Check if the customer_id exists
    cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
    customer = cursor.fetchone()
    if not customer:
        print("Invalid customer ID.")
        return

    # Fetch available drivers with their vehicle information
    cursor.execute("SELECT driver_id, name, vehicle_model FROM drivers WHERE availability = TRUE")
    drivers = cursor.fetchall()

    if not drivers:
        print("No drivers available at the moment.")
        return

    # Display available drivers and their vehicles
    print("\nAvailable Drivers:")
    for index, driver in enumerate(drivers, 1):
        print(f"{index}. {driver[1]} - {driver[2]}")

    # Let the customer choose a driver
    driver_choice = validate_number_input(input("\nSelect a driver by number: "), int)
    if driver_choice is None or driver_choice < 1 or driver_choice > len(drivers):
        print("Invalid driver selection.")
        return

    driver_id = drivers[driver_choice - 1][0]
    driver_name = drivers[driver_choice - 1][1]
    vehicle_model = drivers[driver_choice - 1][2]

    # Calculate fare
    base_fare = 5
    rate_per_km = 2
    fare = base_fare + (rate_per_km * distance)

    # Insert booking into the database
    booking_time = datetime.now()
    cursor.execute("""
        INSERT INTO bookings (customer_id, driver_id, pickup_location, drop_location, distance, fare, booking_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (customer_id, driver_id, pickup_location, drop_location, distance, fare, booking_time))

    # Commit the transaction
    db.commit()

    print(f"\nRide booked successfully with {driver_name} ({vehicle_model}). Fare: ${fare}")

# Function to view ride history for a customer
def view_ride_history(customer_id):
    cursor.execute("""
        SELECT b.booking_id, b.pickup_location, b.drop_location, b.distance, b.fare, b.booking_time, d.name, d.vehicle_model
        FROM bookings b
        JOIN drivers d ON b.driver_id = d.driver_id
        WHERE b.customer_id = %s
    """, (customer_id,))

    rides = cursor.fetchall()

    if not rides:
        print("No ride history found.")
        return

    for ride in rides:
        print(f"Booking ID: {ride[0]}, Pickup: {ride[1]}, Drop: {ride[2]}, Distance: {ride[3]} km, Fare: ${ride[4]}, Time: {ride[5]}, Driver: {ride[6]} - {ride[7]}")

# Function to generate an invoice
def generate_invoice(booking_id):
    cursor.execute("""
        SELECT b.booking_id, c.name AS customer_name, c.phone_number AS customer_phone, 
               d.name AS driver_name, d.vehicle_model, b.pickup_location, 
               b.drop_location, b.distance, b.fare, b.booking_time
        FROM bookings b
        JOIN customers c ON b.customer_id = c.customer_id
        JOIN drivers d ON b.driver_id = d.driver_id
        WHERE b.booking_id = %s
    """, (booking_id,))

    booking = cursor.fetchone()

    if not booking:
        print("Booking not found.")
        return

    # Extracting details from the result
    booking_id, customer_name, customer_phone, driver_name, vehicle_model, \
    pickup_location, drop_location, distance, fare, booking_time = booking

    # Format the invoice in a table-like structure
    print("\n======= Invoice =======")
    print(f"Booking ID: {booking_id}")
    print(f"Customer Name: {customer_name}")
    print(f"Customer Phone: {customer_phone}")
    print(f"Driver Name: {driver_name}")
    print(f"Vehicle Model: {vehicle_model}")
    print(f"Booking Time: {booking_time}")
    
    print("\nTrip Details:")
    print(f"Pickup Location: {pickup_location}")
    print(f"Drop Location: {drop_location}")
    print(f"Distance: {distance} km")
    
    print("\nFare Breakdown:")
    print(f"Base Fare: $5.00")
    print(f"Fare per km: $2.00")
    print(f"Total Fare: ${fare}")
    
    # Insert the invoice into the invoices table
    issue_date = datetime.now()
    cursor.execute("""
        INSERT INTO invoices (booking_id, amount, issue_date)
        VALUES (%s, %s, %s)
    """, (booking_id, fare, issue_date))

    # Commit the transaction
    db.commit()

    print(f"\nInvoice generated successfully for booking ID {booking_id}.")
    print("=======================")

# Function to display the menu and get user input
def display_menu():
    print("\n===== Taxi Booking System =====")
    print("1. Book a Ride")
    print("2. View Ride History")
    print("3. Generate Invoice")
    print("4. Exit")
    choice = input("Please select an option (1-4): ")
    return choice

# Function to handle the user's choice (with validation added)
def handle_choice(choice):
    if choice == '1':
        customer_id = validate_number_input(input("Enter customer ID: "), int)
        if customer_id is None:
            return True

        pickup_location = input("Enter pickup location: ").strip()
        if not pickup_location:
            print("Pickup location cannot be empty.")
            return True
        if any(char.isdigit() for char in pickup_location):
            print("Pickup location cannot contain numbers.")
            return True

        drop_location = input("Enter drop location: ").strip()
        if not drop_location:
            print("Drop location cannot be empty.")
            return True
        if any(char.isdigit() for char in drop_location):
            print("Drop location cannot contain numbers.")
            return True

        if pickup_location.lower() == drop_location.lower():
            print("Pickup and drop locations cannot be the same.")
            return True

        distance = validate_number_input(input("Enter distance (in km): "), float)
        if distance is None:
            return True

        book_ride(customer_id, pickup_location, drop_location, distance)

    elif choice == '2':
        customer_id = validate_number_input(input("Enter customer ID to view ride history: "), int)
        if customer_id is None:
            return True
        view_ride_history(customer_id)

    elif choice == '3':
        booking_id = validate_number_input(input("Enter booking ID to generate invoice: "), int)
        if booking_id is None:
            return True
        generate_invoice(booking_id)

    elif choice == '4':
        print("Exiting the system. Goodbye!")
        return False

    else:
        print("Invalid choice. Please try again.")
    return True

# Main function to run the CLI system
def main():
    # Insert sample data into the database (you can comment this out after the first run)
    insert_sample_drivers()
    insert_sample_customers()
    insert_sample_bookings()

    # Main loop
    while True:
        choice = display_menu()
        if not handle_choice(choice):
            break

if __name__ == "__main__":
    main()
