# Online Judge Project

Welcome to the Online Judge project! This repository contains the latest code updates for the project, including link to the website and a project demo video link.

## Table of Contents
- [Online Judge Project](#online-judge-project)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Features](#features)
  - [Link to the Website](#link-to-the-website)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Demo Video](#demo-video)

## Introduction

The Online Judge project is a web-based platform designed to manage and evaluate coding problems and solutions. It allows users to submit code, run it against predefined test cases, and view their results.

## Features

- User authentication and profiles
- Problem creation and management
- Code submission and evaluation
- Real-time code execution monitoring
- Leaderboards and statistics
- Admin dashboard for managing problems and users

## Link to the Website

Check out the Website [PiCode](https://picode.live/):

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/MA-Husain/Online_Judge.git
   cd online-judge
   ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate # macOS/Linux
    venv\Scripts\activate # Windows
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Create a .env file and add your secret settings (e.g., DJANGO_SECRET_KEY, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD).

5. Run the initial migrations:
    ```sh
    python manage.py makemigrations
    python manage.py migrate
    ```

6. Collect static files:
    ```sh
    python manage.py collectstatic
    ```

7. Start the development server:
    ```sh
    python manage.py runserver
    ```
8. Create SuperUser/Admin (optional):
    ```sh
    manage.py createsuperuser
    ```

## Usage

1. Open your browser and go to http://127.0.0.1:8000/.
2. Sign up for a new account or log in with an existing account.
3. Navigate through the platform to explore its features:
    - View and solve coding problems
    - Submit and evaluate code
    - Check the leaderboard and statistics
    - If you login as admin you also have a tab to create problem.

## Demo Video

Check out the project demo video [Demo](https://drive.google.com/file/d/1NgUNFXybh6u2O_J3h51d4GWeg8OUOwlc/view?usp=sharing)
 
