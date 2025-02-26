---
# Social Media Web App with Python Django

This is a simple social media web app built using Django.


**ER Diagram of the project**
<br> <br>
![image](https://github.com/user-attachments/assets/4d9d57bf-c1ea-45bb-8ca5-ebb2a7c658e0)
## User Credentials for Testing

- **Admin User:**
  - **Username:** admin
  - **Password:** admin
- **Test User:**
  - **Username:** faiyaz
  - **Password:** alhasan75

## Setup and Installation Instructions

Follow these steps to set up and run the application locally:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Faiyazmahmud75/social-media-with-python-django.git
   cd social-media-with-python-django
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Apply the database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the application:**
   Open your web browser and go to `http://127.0.0.1:8000/`

## Summary of Implemented Features

- **User Authentication:**
  - User registration and login

- **User Profiles:**
  - View and edit user profiles
  - Upload & update profile pictures
  - Upload & update cover photos
  - view profile user's posts

- **Posts:**
  - Create, edit, and delete posts
  - Like, comment and share post url on posts

- **Responsive Design:**
  - Mobile-friendly layout using Bootstrap

---

