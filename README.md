# E-commerce Platform Performance Testing

This project is designed to simulate an e-commerce platform where a server handles multiple clients that can register, log in, add products, view products, and place orders. Additionally, performance tests are run under various network conditions such as loss, delay, and bandwidth limitations using `tcconfig` commands. The results are recorded, and performance data is visualized with matplotlib.

## Table of Contents

1. [Project Description](#project-description)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Running the Project](#running-the-project)
5. [Network Performance Testing](#network-performance-testing)
6. [Performance Data and Graphs](#performance-data-and-graphs)
7. [TCP Connections Overview](#tcp-connections-overview)
8. [Team Members](#team-members)

---

## Project Description

This project simulates a simple e-commerce platform with server-client architecture. It is designed to test the performance of the platform under various network conditions:

- **Server**: Handles user registration, login, product management, and order placement.
- **Client**: Interacts with the server to simulate user activities such as registering, logging in, browsing products, and placing orders.
- **Performance Testing**: Uses `tcconfig` to simulate network conditions (packet loss, delay, and bandwidth restrictions) and measures the impact on request latency and round-trip time (RTT). The results are visualized using matplotlib.

The project can be deployed on two virtual machines: one for the server and one for each client.

---

## System Requirements

Before running the project, make sure you have the following:

- **Virtual Machine 1** (for Server):
  - Python 3.x
  - `sqlite3` (for the database)
  - `socket` (for networking)
  - `tcconfig` (for network condition simulation)
  - `pandas` and `matplotlib` (for data visualization)

- **Virtual Machine 2+** (for Clients):
  - Python 3.x
  - `socket` (for networking)
  - `pickle` (for serialization)

---

## Installation

1. Clone this repository to each VM (one for the server and each client):
    ```bash
    git clone https://github.com/suman1406/sE-Commerce-Platform-using-TCP-Connections.git
    cd E-Commerce-Platform-using-TCP-Connections
    ```

2. Install the required Python libraries on both the server and client VMs:
    ```bash
    pip install matplotlib pandas
    ```

3. Install `tcconfig` on the server VM for network condition simulation:
    ```bash
    sudo apt install tcconfig
    ```

4. Set up SQLite database on the server:
    The database will be automatically created when you run the server code, so no additional steps are needed here.

---

## Running the Project

### 1. Run the Server

To run the server, execute the following command on the **server VM**:
```bash
python3 server.py
```

The server will start listening on port 5000. ***The IP address used in the code should be updated to match the server VM's IP.***

### 2. Run the Client

To simulate multiple clients, run the following command on each **client VM**:
```bash
python3 client.py
```

Each client can register, log in, and interact with the e-commerce platform.

---

## Network Performance Testing

The `perform.py` script allows you to simulate different network conditions and test the platform's performance. This script is meant to be run from the **server VM**.

### Steps:

1. **Set IP Addresses**:
    - Make sure the IP addresses in the `perform.py` script are updated to reflect the actual IP address of the server.

2. **Run Performance Tests**:
    ```bash
    python3 perform.py
    ```

3. **View Performance Data**:
   - Performance data will be saved to CSV files, and graphs showing the impact of different network conditions will be generated in the `graphs/` directory.

---

## Performance Data and Graphs

The performance tests simulate network conditions such as:

1. **Packet Loss**: Simulated using the command `tcset --loss`.
2. **Delay**: Simulated using the command `tcset --delay`.
3. **Bandwidth Limitation**: Simulated using the command `tcset --rate`.

Performance data includes:

- **Latency (ms)**: Time taken for each operation (e.g., registration, login) under different conditions.
- **RTT (ms)**: Round-trip time for each request under different conditions.
  
The data is saved as CSV files, and the performance graphs are generated using matplotlib.

---

## TCP Connections Overview

The following table provides an overview of the TCP connections available:

| Connection Type          | Server Port | Client Port | Description                                     |
|--------------------------|-------------|-------------|-------------------------------------------------|
| User Registration         | 5000        | Random      | Clients register with username and password.    |
| User Login                | 5000        | Random      | Clients log in with username and password.      |
| Add Product (Admin Only)  | 5001        | Random      | Admin can add products to the catalog.          |
| View Products             | 5001        | Random      | Clients can browse the product catalog.         |
| Place Order               | 5001        | Random      | Clients can place an order for products.        |

---

## Team Members

- **Suman Panigrahi** (Myself)  
  GitHub: [Link](https://github.com/suman1406)
  
- **Sravani Oruganti**  
  GitHub: [Link](https://github.com/sravs-01)

- **Sai Kiran Varma**  
  <!-- GitHub: [Link] -->

- **Soma Siva Pravallika**  
  <!-- GitHub: [Link] -->

---

## Additional Notes

1. Make sure the IP addresses for the server and clients are correctly updated in all scripts (`server.py`, `client.py`, and `perform.py`).
2. To view performance graphs, navigate to the `graphs/` directory after running `perform.py`.
3. For any issues, refer to the logs generated during the server-client operations.

---
