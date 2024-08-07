# E-commerce Application

This is a simple e-commerce application built with Flask, MongoDB, and Google OAuth. It allows users to register, login, browse products, add items to their cart, checkout, and view their order history. Administrators have access to a dashboard with user management, product management, order management, and reporting features.

## Features

* **User Authentication:**
    * Registration with username, email, and password.
    * Login with username and password.
    * Google OAuth login.
* **Product Management:**
    * Browse products with images.
    * Add new products (admin only).
    * Edit existing products (admin only).
    * Delete products (admin only).
* **Shopping Cart:**
    * Add products to cart.
    * View cart contents.
    * Update cart quantities.
    * Remove items from cart.
* **Checkout:**
    * Place orders.
    * View order history.
* **Admin Dashboard:**
    * View user statistics.
    * View product statistics.
    * View order statistics.
    * Manage users (create, update, delete).
    * Export reports (sales, inventory, etc.).
* **API Endpoints:**
    * User management API.
    * Order management API.

## Installation

1. **Install Python:** Ensure you have Python installed on your system.
2. **Create a virtual environment:**
   ```bash
   python -m venv env

3. **Activate the virtual environment:**
   ```bash
   source env/bin/activate
   env\Scripts\activate 

   pip install -r requirements.txt

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt


5. **Set up environment variables:**
    * Create a .env file in the project root directory.
    * Add the following environment variables:
    ```bash
    SECRET_KEY=your_secret_key
    MONGODB_URI=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/your_database?retryWrites=true&w=majority
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    
    * Replace the placeholders with your actual values.
    
6. **Create a client_secrets.json file:**
   * Download the client_secrets.json file from the Google Cloud Console.
   * Place it in the project root directory.



## **Run the application:**
  1. **Start the Python development server:**
   ```bash
   python app.py

2. **Access the application:**
   *Open your web browser and navigate to http://127.0.0.1:5000/.


## Usage

1. **Access the application:** Open your web browser and navigate to `http://127.0.0.1:5000/`.
2. **Register or login:** Create a new account or login with your existing credentials.
3. **Browse products:** Explore the available products and add them to your cart.
4. **Checkout:** Proceed to checkout and complete your purchase.
5. **View order history:** Access your past orders.

## Admin Dashboard

1. **Login as an administrator:** Use the administrator credentials to access the dashboard.
2. **Manage users:** Create, update, or delete users.
3. **Manage products:** Add, edit, or delete products.
4. **Manage orders:** View and manage orders.
5. **Generate reports:** Export sales, inventory, or other reports.

## Technologies

* **Flask:** Python web framework.
* **MongoDB:** NoSQL database.
* **Google OAuth:** Authentication and authorization.
* **Jinja2:** Templating engine.
* **Tailwind CSS:** CSS framework.
* **JavaScript:** some javascript.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

This README file provides a basic structure for your e-commerce application. You can customize it further to include more details about your project, such as:

* **Deployment instructions:** How to deploy the application to a production environment.
* **Testing instructions:** How to run tests for the application.
* **Additional features:** Any other features that are not mentioned in the basic features list.
* **Screenshots:** Include screenshots of the application's user interface.

Remember to update the README file with relevant information as you develop your e-commerce application.
