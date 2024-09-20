import socket
import time
import datetime
import csv
import matplotlib.pyplot as plt
import os
import pickle
import random
import string
import logging

# E-commerce Server Addresses
SERVER_IP = "192.168.36.130"  # Replace with your server's IP address
USER_SERVER_PORT = 5000
PRODUCT_ORDER_SERVER_PORT = 5001

USER_SERVER_ADDRESS = (SERVER_IP, USER_SERVER_PORT)
PRODUCT_ORDER_SERVER_ADDRESS = (SERVER_IP, PRODUCT_ORDER_SERVER_PORT)

# Global variables for performance data
performance_data = []

# Configure logging
logging.basicConfig(level=logging.INFO)

# Global variables to store user credentials and user_id
registered_users = []

def log_performance(operation, latency, condition_type, condition_value, success):
    data = {
        'timestamp': datetime.datetime.now(),
        'operation': operation,
        'latency_ms': latency * 1000,
        'condition_type': condition_type,
        'condition_value': condition_value,
        'success': success
    }
    performance_data.append(data)

def send_request(server_address, command, data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(server_address)

        # Serialize and send the data
        start_time = time.time()
        client_socket.send(pickle.dumps((command, data)))

        # Receive the response
        response = client_socket.recv(4096)
        end_time = time.time()

        # Deserialize the response
        response_data = pickle.loads(response)
        success = True
    except Exception as e:
        logging.error(f"Error during {command}: {e}")
        end_time = time.time()
        response_data = None
        success = False
    finally:
        client_socket.close()

    latency = end_time - start_time
    return response_data, latency, success

def apply_network_condition(interface, condition_type, value):
    # Reset existing settings
    os.system(f"tcdel --device {interface} --all >/dev/null 2>&1")
    # Apply new condition
    if condition_type == 'loss':
        os.system(f"tcset --device {interface} --loss {value}% >/dev/null 2>&1")
    elif condition_type == 'delay':
        os.system(f"tcset --device {interface} --delay {value}ms >/dev/null 2>&1")
    elif condition_type == 'bandwidth':
        os.system(f"tcset --device {interface} --rate {value}Kbps >/dev/null 2>&1")
    elif condition_type == 'reset':
        os.system(f"tcdel --device {interface} --all >/dev/null 2>&1")
    else:
        logging.error(f"Unknown condition type: {condition_type}")

def run_performance_test(interface, condition_type, values, test_duration):
    global performance_data
    # Clear previous performance data for this condition type
    performance_data = []
    for value in values:
        apply_network_condition(interface, condition_type, value)
        logging.info(f"Testing with {condition_type} = {value}")

        # Run test operations
        simulate_test_operations(test_duration, condition_type, value)

        # Reset network conditions after each test value
        apply_network_condition(interface, 'reset', None)

    # After testing all values for this condition type, save and plot data
    filename = f'performance_{condition_type}.csv'
    save_performance_data(filename)
    plot_performance_graphs(condition_type, values, filename)

def simulate_test_operations(test_duration, condition_type, condition_value):
    start_time = time.time()
    # Login as admin user for product creation
    admin_username = "admin"
    admin_password = "admin"
    admin_user_id = simulate_user_login(admin_username, admin_password, condition_type, condition_value)
    if not admin_user_id:
        logging.error("Admin login failed. Cannot add products.")
        return
    while time.time() - start_time < test_duration:
        # Simulate user registration
        username, password = simulate_user_registration(condition_type, condition_value)
        # Simulate user login
        user_id = simulate_user_login(username, password, condition_type, condition_value)
        # Simulate adding a product if necessary
        ensure_product_exists(admin_user_id, condition_type, condition_value)
        # Simulate product operations
        simulate_product_operations(condition_type, condition_value)
        # Simulate placing an order
        if user_id:
            simulate_place_order(user_id, condition_type, condition_value)

def simulate_user_registration(condition_type, condition_value):
    # Generate a unique username
    username = "user_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    password = "password123"
    response, latency, success = send_request(USER_SERVER_ADDRESS, 'register', (username, password))
    log_performance('register', latency, condition_type, condition_value, success)
    if response != 'User registered successfully':
        logging.warning(f"Registration failed: {response}")
    else:
        registered_users.append((username, password))
    return username, password

def simulate_user_login(username, password, condition_type, condition_value):
    response, latency, success = send_request(USER_SERVER_ADDRESS, 'login', (username, password))
    log_performance('login', latency, condition_type, condition_value, success)
    if success and isinstance(response, tuple) and response[0] == 'Login successful':
        user_info = response[1]
        user_id = user_info['user_id']
        return user_id
    else:
        logging.warning(f"Login failed: {response}")
        return None

def ensure_product_exists(admin_user_id, condition_type, condition_value):
    # Check if there are products with sufficient stock
    response, latency, success = send_request(PRODUCT_ORDER_SERVER_ADDRESS, 'view_products', None)
    if success and response:
        product_exists = any(product[4] > 0 for product in response)
    else:
        product_exists = False

    if not product_exists:
        # Create a new product with sufficient stock
        product_name = "TestProduct_" + ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        category = "TestCategory"
        price = random.uniform(10.0, 100.0)
        stock = 100  # Set a high stock level
        product_data = (product_name, category, price, stock)
        response, latency, success = send_request(PRODUCT_ORDER_SERVER_ADDRESS, 'add_product', (admin_user_id, product_data))
        log_performance('add_product', latency, condition_type, condition_value, success)
        if success and response == 'Product added successfully':
            logging.info(f"Added product {product_name} with stock {stock}")
        else:
            logging.warning(f"Failed to add product: {response}")

def simulate_product_operations(condition_type, condition_value):
    response, latency, success = send_request(PRODUCT_ORDER_SERVER_ADDRESS, 'view_products', None)
    log_performance('view_products', latency, condition_type, condition_value, success)
    if not response:
        logging.warning("No products received or error occurred.")
    else:
        # Store available products for order placement
        global available_products
        available_products = response

def simulate_place_order(user_id, condition_type, condition_value):
    # Select a product with sufficient stock
    product_id = None
    for product in available_products:
        if product[4] > 0:  # product[4] is stock
            product_id = product[0]  # product[0] is product ID
            break
    if not product_id:
        logging.warning("No products with sufficient stock available.")
        return

    items = [(product_id, 1)]  # Order 1 unit of selected product
    response, latency, success = send_request(PRODUCT_ORDER_SERVER_ADDRESS, 'place_order', (user_id, items))
    log_performance('place_order', latency, condition_type, condition_value, success)
    if not success or not isinstance(response, tuple) or response[0] != 'Order placed successfully':
        logging.warning(f"Order placement failed: {response}")
    else:
        # Simulate submitting a rating
        rating_data = ('submit_rating', 5)  # Giving a rating of 5
        response, latency, success = send_request(PRODUCT_ORDER_SERVER_ADDRESS, 'submit_rating', (response[1]['order_id'], 5))
        log_performance('submit_rating', latency, condition_type, condition_value, success)

def save_performance_data(filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['timestamp', 'operation', 'latency_ms', 'condition_type', 'condition_value', 'success']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in performance_data:
            writer.writerow(entry)
    logging.info(f"Performance data saved to '{filename}'.")

def plot_performance_graphs(condition_type, values, filename):
    try:
        # Read data from CSV
        data_by_operation = {}
        data_by_condition_value = {}
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                operation = row['operation']
                condition_value = float(row['condition_value'])
                success = row['success'] == 'True'
                if success:
                    latency = float(row['latency_ms'])
                    # Collect data per operation
                    if operation not in data_by_operation:
                        data_by_operation[operation] = {}
                    if condition_value not in data_by_operation[operation]:
                        data_by_operation[operation][condition_value] = []
                    data_by_operation[operation][condition_value].append(latency)
                    # Collect data per condition value
                    if condition_value not in data_by_condition_value:
                        data_by_condition_value[condition_value] = []
                    data_by_condition_value[condition_value].append(latency)
        # Sort values for plotting
        sorted_values = sorted(values)
        # Plot all operations in one graph
        plt.figure()
        for operation in data_by_operation:
            avg_latencies = []
            for value in sorted_values:
                latencies = data_by_operation[operation].get(value, [])
                avg_latency = sum(latencies)/len(latencies) if latencies else 0
                avg_latencies.append(avg_latency)
            plt.plot(sorted_values, avg_latencies, marker='o', label=operation)
        plt.xlabel(f'{condition_type.capitalize()}')
        plt.ylabel('Average Latency (ms)')
        plt.title(f'Average Latency vs {condition_type.capitalize()}')
        plt.legend()
        plt.grid(True)
        dir_name = f'graphs/{condition_type}'
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        image_path = f'{dir_name}/latency_vs_{condition_type}.png'
        plt.savefig(image_path)
        plt.close()
        logging.info(f"Graph saved: {image_path}")

        # Plot overall average latency vs condition value
        avg_overall_latencies = []
        for value in sorted_values:
            latencies = data_by_condition_value.get(value, [])
            avg_latency = sum(latencies)/len(latencies) if latencies else 0
            avg_overall_latencies.append(avg_latency)
        plt.figure()
        plt.plot(sorted_values, avg_overall_latencies, marker='o')
        plt.xlabel(f'{condition_type.capitalize()}')
        plt.ylabel('Average Latency (ms)')
        plt.title(f'Overall Average Latency vs {condition_type.capitalize()}')
        plt.grid(True)
        image_path = f'{dir_name}/overall_latency_vs_{condition_type}.png'
        plt.savefig(image_path)
        plt.close()
        logging.info(f"Overall average latency graph saved: {image_path}")

    except Exception as e:
        logging.error(f"Error in plotting performance graphs: {e}")

if __name__ == "__main__":
    interface = 'ens33'  # Replace with your network interface

    # Ensure tcconfig is installed
    if os.system("which tcset >/dev/null 2>&1") != 0:
        logging.error("tcconfig is not installed. Please install it to run network condition tests.")
    else:
        # Run performance tests with different network conditions

        # Test for loss percentages
        run_performance_test(interface, 'loss', [0, 1, 2], test_duration=30)

        # Test for different delays
        run_performance_test(interface, 'delay', [0, 50, 100], test_duration=30)

        # Test for different bandwidths
        run_performance_test(interface, 'bandwidth', [1000, 500, 100], test_duration=30)

