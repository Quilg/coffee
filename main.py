import sqlite3
from faker import Faker
from datetime import date
import csv

fake = Faker()
conn = sqlite3.connect('coffee_shop.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        address TEXT,
        phone_number TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        description TEXT NOT NULL,
        order_date DATE NOT NULL,
        total_amount INTEGER NOT NULL,
        completed BOOLEAN DEFAULT 0,
        clerk_id INTEGER,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (clerk_id) REFERENCES employees(employee_id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        employee_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
''')

conn.commit()

# for _ in range(100):
#     cursor.execute("INSERT INTO customers (name, address, phone_number) VALUES (?, ?, ?)",
#                    (fake.name(), fake.address(), fake.phone_number()))
# conn.commit()
# conn.close()

#since the database is already created, we will comment this line out. All of the logins and passwords can be found inside the employees.csv

def login(username, password):
    conn = sqlite3.connect('coffee_shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM employees WHERE username=? AND password=?", (username, password))
    role = cursor.fetchone()
    conn.close()
    return role[0] if role else None

def clerk_menu():
    while True:
        print("\nMenu for Clerks:")
        print("1. Add order")
        print("2. Add order (new customer)")
        print("3. Assign order to delivery")
        print("4. View pending orders")
        print("5. Exit")
        choice = input("Select the number: ")
        if choice == '1':
            customer_id = int(input("Enter customer ID: "))
            description = input("Enter order description: ")
            total_amount = int(input("Enter amount: "))
            clerk_id = int(input("Enter your clerk ID: "))
            add_order(customer_id, description, total_amount, clerk_id)
            print("\nOrder was added successfully!")
        elif choice == '2':
            name = input("Enter customer name: ")
            address = input("Enter customer address: ")
            phone_number = input("Enter customer phone number: ")
            customer_id = add_new_customer(name, address, phone_number)
            description = input("Enter order description: ")
            total_amount = int(input("Enter amount: "))
            clerk_id = int(input("Enter your clerk ID: "))
            add_order(customer_id, description, total_amount, clerk_id)
            print("\nOrder was added successfully!")
        elif choice == '3':
            order_id = int(input("Enter order ID: "))
            delivery_employee_id = int(input("Enter delivery employee ID: "))
            assign_order(order_id, delivery_employee_id)
            print("\nOrder was successfully assigned to delivery!")
        elif choice == '4':
            view_pending_orders()
        elif choice == '5':
            break
        else:
            print("Wrong choice!")

def add_new_customer(name, address, phone_number):
    conn = sqlite3.connect('coffee_shop.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO customers (name, address, phone_number) VALUES (?, ?, ?)", (name, address, phone_number))
    customer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return customer_id

def view_pending_orders():
    conn = sqlite3.connect('coffee_shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE completed=0")
    orders = cursor.fetchall()
    if not orders:
        print("\nNo pending orders.")
    else:
        print("\nPending Orders:")
        for order in orders:
            print(f"Order ID: {order[0]}, Description: {order[2]}, Amount: {order[4]}")

def add_order(customer_id, description, total_amount, clerk_id):
    conn = sqlite3.connect('coffee_shop.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (customer_id, description, order_date, total_amount, clerk_id) VALUES (?, ?, ?, ?, ?)",
                   (customer_id, description, date.today(), total_amount, clerk_id))
    conn.commit()
    conn.close()

def assign_order(order_id, delivery_employee_id):
    conn = sqlite3.connect('coffee_shop.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET clerk_id=null, completed=0 WHERE order_id=?", (order_id,))
    cursor.execute("UPDATE orders SET clerk_id=? WHERE order_id=?", (delivery_employee_id, order_id))
    conn.commit()
    conn.close()

def delivery_menu():
    while True:
        print("\nMenu for delivery:")
        print("1. Mark order as completed")
        print("2. Your pending deliveries")
        print("3. Exit")

        choice = input("Select the number: ")

        if choice == '1':
            order_id = int(input("Enter order ID: "))
            complete_order(order_id)
            print("\nOrder was completed successfully!")
        elif choice == '2':
            view_pending_orders()
        elif choice == '3':
            break
        else:
            print("\nWrong choice!")

def complete_order(order_id):
    conn = sqlite3.connect('coffee_shop.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET completed=1 WHERE order_id=?", (order_id,))
    conn.commit()
    conn.close()

def manager_menu():
    while True:
        print("\nMenu for managers:")
        print("1. Customer profile")
        print("2. Orders on day")
        print("3. Orders set by clerk")
        print("4. Pending orders")
        print("5. View Customers (exports to csv)")
        print("6. View Employees (exports to csv)")
        print("7. View Orders (exports to csv)")
        print("8. Exit")

        choice = input("Select the number: ")

        if choice == '1':
            customer_profile()
        elif choice == '2':
            orders_on_day()
        elif choice == '3':
            orders_set_by_clerk()
        elif choice == '4':
            view_pending_orders()
        elif choice == '5':
            export_to_csv('customers')
        elif choice == '6':
            export_to_csv('employees')
        elif choice == '7':
            export_to_csv('orders')
        elif choice == '8':
            break
        else:
            print("\nWrong choice!")

def customer_profile():
    customer_id = int(input("Enter customer ID: "))
    conn = sqlite3.connect('coffee_shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE customer_id=?", (customer_id,))
    customer = cursor.fetchone()
    cursor.execute("SELECT COUNT(order_id), SUM(total_amount) FROM orders WHERE customer_id=?", (customer_id,))
    order_stats = cursor.fetchone()
    conn.close()
    if not customer:
        print("\nCustomer does not exist.")
    else:
        print("\nCustomer Profile:")
        print(f"Customer ID: {customer[0]}, Name: {customer[1]}, Address: {customer[2]}, Phone Number: {customer[3]}")
        print(f"Total Orders: {order_stats[0]}, Total Amount Paid: {order_stats[1]}")

def orders_on_day():
    order_date = input("Enter date (YYYY-MM-DD): ")
    conn = sqlite3.connect('coffee_shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE order_date=?", (order_date,))
    orders = cursor.fetchall()
    conn.close()
    if not orders:
        print(f"\nThere were no orders on {order_date}.")
    else:
        print(f"\nOrders on {order_date}:")
        for order in orders:
            print(f"\nOrder ID: {order[0]}, Description: {order[2]}, Amount ordered: {order[4]}")

def orders_set_by_clerk():
    clerk_id = int(input("Enter clerk ID: "))
    conn = sqlite3.connect('coffee_shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE clerk_id=?", (clerk_id,))
    orders = cursor.fetchall()
    conn.close()
    if not orders:
        print(f"\nNo orders were set by this clerk.")
    else:
        print("\nOrders set by this clerk:")
        for order in orders:
            print(f"\nOrder ID: {order[0]}, Description: {order[2]}, Amount: {order[4]}")


def export_to_csv(table_name):
    conn = sqlite3.connect('coffee_shop.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    data = cursor.fetchall()
    conn.close()
    filename = f"{table_name}.csv"
    with open(filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([i[0] for i in cursor.description])
        csv_writer.writerows(data)

    print("\nData was exported successfuly!")

while True:
    print("\nLogin Menu:")
    username = input("Username: ")
    password = input("Password: ")
    role = login(username, password)
    if role == 'clerk':
        clerk_menu()
    elif role == 'delivery':
        delivery_menu()
    elif role == 'manager':
        manager_menu()
    else:
        print("\nWrong username or password!")
