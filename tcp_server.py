import socket
import threading
import sqlite3
import pickle
import traceback

# Initialize the SQLite database connection
conn = sqlite3.connect('ecommerce.db', check_same_thread=False)
cursor = conn.cursor()

# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

# Create necessary tables and admin user
def create_tables():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS OrderHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            order_timestamp TEXT,
            rating INTEGER,
            FOREIGN KEY(user_id) REFERENCES User(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS OrderItem (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY(order_id) REFERENCES OrderHistory(id),
            FOREIGN KEY(product_id) REFERENCES Product(id)
        )
    ''')
    conn.commit()

    # Check if admin user exists; if not, create it
    cursor.execute("SELECT * FROM User WHERE username = ?", (ADMIN_USERNAME,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO User (username, password, is_admin) VALUES (?, ?, ?)",
                       (ADMIN_USERNAME, ADMIN_PASSWORD, 1))
        conn.commit()
        print(f"Admin user '{ADMIN_USERNAME}' created with password '{ADMIN_PASSWORD}'.")
    else:
        print(f"Admin user '{ADMIN_USERNAME}' already exists.")

# Handle client requests
def handle_client(client_socket):
    try:
        while True:
            # Receive request data from the client
            request_data = client_socket.recv(4096)
            if not request_data:
                break

            # Unpack the request data
            command, data = pickle.loads(request_data)

            if command == 'register':
                username, password = data
                try:
                    cursor.execute("INSERT INTO User (username, password) VALUES (?, ?)", (username, password))
                    conn.commit()
                    response = 'User registered successfully'
                except sqlite3.IntegrityError:
                    response = 'Username already exists'
                client_socket.send(pickle.dumps(response))

            elif command == 'login':
                username, password = data
                cursor.execute("SELECT id, is_admin FROM User WHERE username = ? AND password = ?", (username, password))
                user = cursor.fetchone()
                if user:
                    user_id, is_admin = user
                    response = ('Login successful', {'user_id': user_id, 'is_admin': bool(is_admin)})
                else:
                    response = 'Invalid credentials'
                client_socket.send(pickle.dumps(response))

            elif command == 'change_password':
                user_id, old_password, new_password = data
                cursor.execute("SELECT password FROM User WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                if user and user[0] == old_password:
                    cursor.execute("UPDATE User SET password = ? WHERE id = ?", (new_password, user_id))
                    conn.commit()
                    response = 'Password updated successfully'
                else:
                    response = 'Invalid user ID or password'
                client_socket.send(pickle.dumps(response))

            elif command == 'add_product':
                user_id, product_data = data
                cursor.execute("SELECT is_admin FROM User WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                if user and user[0]:
                    name, category, price, stock = product_data
                    cursor.execute("INSERT INTO Product (name, category, price, stock) VALUES (?, ?, ?, ?)",
                                   (name, category, price, stock))
                    conn.commit()
                    response = 'Product added successfully'
                else:
                    response = 'Unauthorized: Only admin can add products'
                client_socket.send(pickle.dumps(response))

            elif command == 'view_categories':
                cursor.execute("SELECT DISTINCT category FROM Product")
                categories = [row[0] for row in cursor.fetchall()]
                client_socket.send(pickle.dumps(categories))

            elif command == 'view_products':
                category = data
                if category:
                    cursor.execute("SELECT * FROM Product WHERE category = ?", (category,))
                else:
                    cursor.execute("SELECT * FROM Product")
                products = cursor.fetchall()
                client_socket.send(pickle.dumps(products))

            elif command == 'place_order':
                user_id, items = data
                # Create a new order
                cursor.execute("INSERT INTO OrderHistory (user_id, order_timestamp) VALUES (?, datetime('now'))", (user_id,))
                order_id = cursor.lastrowid

                total_price = 0
                order_success = True  # Flag to check if order can be processed
                for product_id, quantity in items:
                    # Check product availability
                    cursor.execute("SELECT price, stock FROM Product WHERE id = ?", (product_id,))
                    product = cursor.fetchone()
                    if not product:
                        response = f'Product with ID {product_id} not found'
                        order_success = False
                        break
                    price, stock = product
                    if stock < quantity:
                        response = f'Not enough stock for product ID {product_id}'
                        order_success = False
                        break
                    # Deduct stock and add order item
                    cursor.execute("UPDATE Product SET stock = stock - ? WHERE id = ?", (quantity, product_id))
                    cursor.execute("INSERT INTO OrderItem (order_id, product_id, quantity) VALUES (?, ?, ?)",
                                   (order_id, product_id, quantity))
                    total_price += price * quantity

                if order_success:
                    conn.commit()
                    response = ('Order placed successfully', {'order_id': order_id, 'total_price': total_price})
                    client_socket.send(pickle.dumps(response))
                    # Receive rating from client
                    rating_data = client_socket.recv(4096)
                    rating_command, rating = pickle.loads(rating_data)
                    if rating_command == 'submit_rating':
                        cursor.execute("UPDATE OrderHistory SET rating = ? WHERE id = ?", (rating, order_id))
                        conn.commit()
                        response = 'Rating submitted successfully'
                    else:
                        response = 'Rating not submitted'
                    client_socket.send(pickle.dumps(response))
                else:
                    conn.rollback()
                    client_socket.send(pickle.dumps(response))

            elif command == 'view_order_history':
                user_id = data
                cursor.execute("SELECT * FROM OrderHistory WHERE user_id = ?", (user_id,))
                orders = cursor.fetchall()
                order_list = []
                for order in orders:
                    order_id, user_id, timestamp, rating = order
                    cursor.execute("SELECT product_id, quantity FROM OrderItem WHERE order_id = ?", (order_id,))
                    items = cursor.fetchall()
                    order_items = []
                    for product_id, quantity in items:
                        cursor.execute("SELECT name, price FROM Product WHERE id = ?", (product_id,))
                        product = cursor.fetchone()
                        product_name, price = product
                        order_items.append({
                            'product_name': product_name,
                            'quantity': quantity,
                            'unit_price': price,
                            'total_price': round(price * quantity, 2)
                        })
                    order_list.append({
                        'order_id': order_id,
                        'timestamp': timestamp,
                        'rating': rating,
                        'items': order_items
                    })
                client_socket.send(pickle.dumps(order_list))

            else:
                response = 'Unknown command'
                client_socket.send(pickle.dumps(response))

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
    finally:
        client_socket.close()

# Server setup
def server_program():
    create_tables()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 5000))
    server_socket.listen(5)
    print("Server listening on port 5000")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    server_program()

