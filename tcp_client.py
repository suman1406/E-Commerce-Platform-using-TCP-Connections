import socket
import pickle
import time
import csv
import datetime

# Server IP and Ports
SERVER_IP = '192.168.36.130'  # Replace with your server's IP address
USER_SERVER_PORT = 5000        # Port for User-related operations
PRODUCT_ORDER_SERVER_PORT = 5001  # Port for Product and Order-related operations

performance_data = []  # List to store performance data

class User:
    def __init__(self):
        self.logged_in = False
        self.user_id = None
        self.is_admin = False

    def register(self):
        username = input("Enter a username: ")
        password = input("Enter a password: ")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as register_socket:
            register_socket.connect((SERVER_IP, USER_SERVER_PORT))
            operation = 'register'
            start_time = time.time()
            total_rtt = 0
            rtt_count = 0

            # Send request
            request_data = (operation, (username, password))
            rtt_start = time.time()
            register_socket.send(pickle.dumps(request_data))
            response = register_socket.recv(4096)
            rtt_end = time.time()
            rtt = rtt_end - rtt_start
            total_rtt += rtt
            rtt_count += 1

            end_time = time.time()
            latency = end_time - start_time
            response = pickle.loads(response)
            print(response)
            print(f"Latency for {operation}: {latency * 1000:.2f} ms")
            print(f"RTT for {operation}: {rtt * 1000:.2f} ms")
            # Record performance data
            avg_rtt = total_rtt / rtt_count if rtt_count > 0 else 0
            performance_data.append({
                'timestamp': datetime.datetime.now(),
                'operation': operation,
                'latency_ms': latency * 1000,
                'avg_rtt_ms': avg_rtt * 1000
            })

    def login(self):
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as login_socket:
            login_socket.connect((SERVER_IP, USER_SERVER_PORT))
            operation = 'login'
            start_time = time.time()
            total_rtt = 0
            rtt_count = 0

            # Send request
            request_data = (operation, (username, password))
            rtt_start = time.time()
            login_socket.send(pickle.dumps(request_data))
            response = login_socket.recv(4096)
            rtt_end = time.time()
            rtt = rtt_end - rtt_start
            total_rtt += rtt
            rtt_count += 1

            end_time = time.time()
            latency = end_time - start_time
            response = pickle.loads(response)
            if isinstance(response, tuple) and response[0] == 'Login successful':
                print(response[0])
                user_info = response[1]
                self.logged_in = True
                self.user_id = user_info['user_id']
                self.is_admin = user_info['is_admin']
                if self.is_admin:
                    print("Admin access granted.")
            else:
                print(response)
            print(f"Latency for {operation}: {latency * 1000:.2f} ms")
            print(f"RTT for {operation}: {rtt * 1000:.2f} ms")
            # Record performance data
            avg_rtt = total_rtt / rtt_count if rtt_count > 0 else 0
            performance_data.append({
                'timestamp': datetime.datetime.now(),
                'operation': operation,
                'latency_ms': latency * 1000,
                'avg_rtt_ms': avg_rtt * 1000
            })

    def logout(self):
        self.logged_in = False
        self.user_id = None
        self.is_admin = False
        print("You have been logged out.")

    def change_password(self):
        old_password = input("Enter your current password: ")
        new_password = input("Enter your new password: ")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as change_pass_socket:
            change_pass_socket.connect((SERVER_IP, USER_SERVER_PORT))
            operation = 'change_password'
            start_time = time.time()
            total_rtt = 0
            rtt_count = 0

            # Send request
            request_data = (operation, (self.user_id, old_password, new_password))
            rtt_start = time.time()
            change_pass_socket.send(pickle.dumps(request_data))
            response = change_pass_socket.recv(4096)
            rtt_end = time.time()
            rtt = rtt_end - rtt_start
            total_rtt += rtt
            rtt_count += 1

            end_time = time.time()
            latency = end_time - start_time
            response = pickle.loads(response)
            print(response)
            print(f"Latency for {operation}: {latency * 1000:.2f} ms")
            print(f"RTT for {operation}: {rtt * 1000:.2f} ms")
            # Record performance data
            avg_rtt = total_rtt / rtt_count if rtt_count > 0 else 0
            performance_data.append({
                'timestamp': datetime.datetime.now(),
                'operation': operation,
                'latency_ms': latency * 1000,
                'avg_rtt_ms': avg_rtt * 1000
            })

class Product:
    def __init__(self, user):
        self.user = user

    def view_categories(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as category_socket:
            category_socket.connect((SERVER_IP, PRODUCT_ORDER_SERVER_PORT))
            operation = 'view_categories'
            start_time = time.time()
            total_rtt = 0
            rtt_count = 0

            # Send request
            request_data = (operation, None)
            rtt_start = time.time()
            category_socket.send(pickle.dumps(request_data))
            response = category_socket.recv(4096)
            rtt_end = time.time()
            rtt = rtt_end - rtt_start
            total_rtt += rtt
            rtt_count += 1

            end_time = time.time()
            latency = end_time - start_time
            response = pickle.loads(response)
            if response:
                print("Available categories:")
                for idx, category in enumerate(response, start=1):
                    print(f"{idx}. {category}")
                category_choice = input("Select a category number (or press Enter to view all products): ")
                if category_choice:
                    try:
                        category_choice = int(category_choice)
                        if 1 <= category_choice <= len(response):
                            selected_category = response[category_choice - 1]
                            self.view_products(selected_category)
                        else:
                            print("Invalid category selection.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                else:
                    self.view_products(None)
            else:
                print("No categories available.")
            print(f"Latency for {operation}: {latency * 1000:.2f} ms")
            print(f"RTT for {operation}: {rtt * 1000:.2f} ms")
            # Record performance data
            avg_rtt = total_rtt / rtt_count if rtt_count > 0 else 0
            performance_data.append({
                'timestamp': datetime.datetime.now(),
                'operation': operation,
                'latency_ms': latency * 1000,
                'avg_rtt_ms': avg_rtt * 1000
            })

    def view_products(self, category):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as product_socket:
            product_socket.connect((SERVER_IP, PRODUCT_ORDER_SERVER_PORT))
            operation = 'view_products'
            start_time = time.time()
            total_rtt = 0
            rtt_count = 0

            # Send request
            request_data = (operation, category)
            rtt_start = time.time()
            product_socket.send(pickle.dumps(request_data))
            response = product_socket.recv(4096)
            rtt_end = time.time()
            rtt = rtt_end - rtt_start
            total_rtt += rtt
            rtt_count += 1

            end_time = time.time()
            latency = end_time - start_time
            response = pickle.loads(response)
            if response:
                print("Products:")
                for product in response:
                    print(f"ID: {product[0]}, Name: {product[1]}, Category: {product[2]}, Price: ${product[3]}, Stock: {product[4]}")
            else:
                print("No products available.")
            print(f"Latency for {operation}: {latency * 1000:.2f} ms")
            print(f"RTT for {operation}: {rtt * 1000:.2f} ms")
            # Record performance data
            avg_rtt = total_rtt / rtt_count if rtt_count > 0 else 0
            performance_data.append({
                'timestamp': datetime.datetime.now(),
                'operation': operation,
                'latency_ms': latency * 1000,
                'avg_rtt_ms': avg_rtt * 1000
            })

    def add_product(self):
        if not self.user.is_admin:
            print("You must be an admin to add products.")
            return
        name = input("Enter the product name: ")
        category = input("Enter the product category: ")
        price = float(input("Enter the product price: "))
        stock = int(input("Enter the product stock: "))
        product_data = (name, category, price, stock)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as add_product_socket:
            add_product_socket.connect((SERVER_IP, PRODUCT_ORDER_SERVER_PORT))
            operation = 'add_product'
            start_time = time.time()
            total_rtt = 0
            rtt_count = 0

            # Send request
            request_data = (operation, (self.user.user_id, product_data))
            rtt_start = time.time()
            add_product_socket.send(pickle.dumps(request_data))
            response = add_product_socket.recv(4096)
            rtt_end = time.time()
            rtt = rtt_end - rtt_start
            total_rtt += rtt
            rtt_count += 1

            end_time = time.time()
            latency = end_time - start_time
            response = pickle.loads(response)
            print(response)
            print(f"Latency for {operation}: {latency * 1000:.2f} ms")
            print(f"RTT for {operation}: {rtt * 1000:.2f} ms")
            # Record performance data
            avg_rtt = total_rtt / rtt_count if rtt_count > 0 else 0
            performance_data.append({
                'timestamp': datetime.datetime.now(),
                'operation': operation,
                'latency_ms': latency * 1000,
                'avg_rtt_ms': avg_rtt * 1000
            })

class Order:
    def __init__(self, user):
        self.user = user

    def place_order(self):
        cart = []
        while True:
            product_id = input("Enter the product ID you want to buy (or 'done' to finish): ")
            if product_id.lower() == 'done':
                break
            quantity = input("Enter the quantity: ")
            try:
                cart.append((int(product_id), int(quantity)))
            except ValueError:
                print("Invalid input. Please enter valid product ID and quantity.")
        if not cart:
            print("No items in cart. Order cancelled.")
            return
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as order_socket:
            order_socket.connect((SERVER_IP, PRODUCT_ORDER_SERVER_PORT))
            operation = 'place_order'
            start_time = time.time()
            total_rtt = 0
            rtt_count = 0

            # Send order request
            request_data = (operation, (self.user.user_id, cart))
            rtt_start = time.time()
            order_socket.send(pickle.dumps(request_data))
            response = order_socket.recv(4096)
            rtt_end = time.time()
            rtt = rtt_end - rtt_start
            total_rtt += rtt
            rtt_count += 1

            response = pickle.loads(response)
            if isinstance(response, tuple) and response[0] == 'Order placed successfully':
                print(response[0])
                order_info = response[1]
                print(f"Order ID: {order_info['order_id']}, Total Price: ${order_info['total_price']:.2f}")
                # Prompt for rating
                while True:
                    rating = input("Please rate your shopping experience (1-5): ")
                    try:
                        rating = int(rating)
                        if 1 <= rating <= 5:
                            break
                        else:
                            print("Please enter a rating between 1 and 5.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                # Send rating
                rating_data = ('submit_rating', rating)
                rtt_start = time.time()
                order_socket.send(pickle.dumps(rating_data))
                rating_response = order_socket.recv(4096)
                rtt_end = time.time()
                rating_rtt = rtt_end - rtt_start
                total_rtt += rating_rtt
                rtt_count += 1

                rating_response = pickle.loads(rating_response)
                print(rating_response)
            else:
                print(response)

            end_time = time.time()
            latency = end_time - start_time
            print(f"Latency for {operation}: {latency * 1000:.2f} ms")
            avg_rtt = total_rtt / rtt_count if rtt_count > 0 else 0
            print(f"Average RTT for {operation}: {avg_rtt * 1000:.2f} ms")
            # Record performance data
            performance_data.append({
                'timestamp': datetime.datetime.now(),
                'operation': operation,
                'latency_ms': latency * 1000,
                'avg_rtt_ms': avg_rtt * 1000
            })

    def view_order_history(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as order_history_socket:
            order_history_socket.connect((SERVER_IP, PRODUCT_ORDER_SERVER_PORT))
            operation = 'view_order_history'
            start_time = time.time()
            total_rtt = 0
            rtt_count = 0

            # Send request
            request_data = (operation, self.user.user_id)
            rtt_start = time.time()
            order_history_socket.send(pickle.dumps(request_data))
            response = order_history_socket.recv(4096)
            rtt_end = time.time()
            rtt = rtt_end - rtt_start
            total_rtt += rtt
            rtt_count += 1

            end_time = time.time()
            latency = end_time - start_time
            response = pickle.loads(response)
            if response:
                for order in response:
                    print(f"\nOrder ID: {order['order_id']}, Date: {order['timestamp']}, Rating: {order['rating']}")
                    for item in order['items']:
                        print(f"  {item['product_name']} x {item['quantity']} @ ${item['unit_price']} each = ${item['total_price']}")
            else:
                print("No orders found.")
            print(f"Latency for {operation}: {latency * 1000:.2f} ms")
            print(f"RTT for {operation}: {rtt * 1000:.2f} ms")
            # Record performance data
            avg_rtt = total_rtt / rtt_count if rtt_count > 0 else 0
            performance_data.append({
                'timestamp': datetime.datetime.now(),
                'operation': operation,
                'latency_ms': latency * 1000,
                'avg_rtt_ms': avg_rtt * 1000
            })

def save_performance_data():
    if performance_data:
        with open('performance_data.csv', 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'operation', 'latency_ms', 'avg_rtt_ms']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for data in performance_data:
                writer.writerow(data)
        print("Performance data saved to 'performance_data.csv'.")
    else:
        print("No performance data to save.")

def main_menu():
    user = User()
    product = Product(user)
    order = Order(user)

    while True:
        print("\n--- E-commerce Platform ---")
        if not user.logged_in:
            print("1. Register")
            print("2. Log in")
            print("3. Browse Products")
            print("4. Exit")
            choice = input("Select an option: ")

            if choice == '1':
                user.register()
            elif choice == '2':
                user.login()
            elif choice == '3':
                product.view_categories()
            elif choice == '4':
                print("Thank you for using the e-commerce platform. Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")
        else:
            print("1. Browse Products")
            print("2. Place an Order")
            if user.is_admin:
                print("3. Add a Product (Admin only)")
                print("4. Change Password")
                print("5. View Order History")
                print("6. Logout")
                print("7. Exit")
            else:
                print("3. Change Password")
                print("4. View Order History")
                print("5. Logout")
                print("6. Exit")
            choice = input("Select an option: ")

            if choice == '1':
                product.view_categories()
            elif choice == '2':
                order.place_order()
            elif choice == '3' and user.is_admin:
                product.add_product()
            elif (choice == '3' and not user.is_admin) or (choice == '4' and user.is_admin):
                user.change_password()
            elif (choice == '4' and not user.is_admin) or (choice == '5' and user.is_admin):
                order.view_order_history()
            elif (choice == '5' and not user.is_admin) or (choice == '6' and user.is_admin):
                user.logout()
            elif (choice == '6' and not user.is_admin) or (choice == '7' and user.is_admin):
                print("Thank you for using the e-commerce platform. Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")

    # Save performance data at the end
    save_performance_data()

if __name__ == "__main__":
    main_menu()

