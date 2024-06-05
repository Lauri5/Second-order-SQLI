# Demonstration of an Application Vulnerable to Second Order SQL Injection

## Introduction
This repository contains a Flask application designed to demonstrate a second-order SQL injection vulnerability. Such vulnerabilities allow attackers to inject malicious SQL statements that are stored and later executed. The application includes basic functionalities like user registration, login, password reset, and displaying current users.

## Features
- User Registration
- User Login
- Password Reset
- Display of Current Users

## How to Run
1. Clone the repository `git clone https://github.com/Lauri5/Second-order-SQLI.git`
2. Install Flask: `pip install Flask`
3. Run the application: `python app.py`
4. Open a web browser and navigate to `http://127.0.0.1:5000/` or `http://localhost:5000/` to interact with the application.

## Example of an Attack
To demonstrate the vulnerability:
1. Register a user with the username: `admin` and the password: `password123`.
2. Register another user with the username: `admin' --` and any password.
3. Log in as the second user and use the "Reset Password" functionality to change the password to `hacked`.
4. The SQL query executed will be `UPDATE users SET password='hacked' WHERE username='admin' --'`, effectively changing the password for the first user due to SQL comment syntax (`--`), which nullifies the rest of the query.

## Caution
This application is designed for educational purposes only and intentionally contains security vulnerabilities. **Do not deploy this application in a production environment.**

## License
This project is licensed under the MIT license.
