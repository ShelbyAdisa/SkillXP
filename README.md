# SkillXP Nexus: The Connected School Ecosystem

A unified, gamified, and transparent school platform that connects students, educators, and parents, designed to tackle dropouts, boost engagement, ensure safety, and rebuild community trust. SkillXP Nexus transforms the school into a living digital ecosystem.

-----

## Core Features and Modules

The system is built on a modular, service-oriented architecture integrating several key applications (Django Apps):

| Module | Functionality | Key Features |
| :--- | :--- | :--- |
| **SkillXP Learning Hub (LMS)** | Gamified Learning and Classroom Management | Classrooms, Assignments, Submissions, Gradebook, XP Rewards, and Leaderboards. |
| **eLibrary** | Centralized, AI-curated resource library | Personalized recommendations, search functionality, and resource organization/categorization. |
| **Wellbeing Hub** | Anonymous Support System | Anonymous counseling spaces, mood checking, goal tracking, and AI-driven crisis alerts and toxicity detection. |
| **Social / Community** | Reddit-style open forums | Interest-based groups, posts, comments, upvoting, and peer mentorship features. |
| **Rewards & Gamification** | XP Economy and User Engagement | Students earn XP for tasks, level up, and redeem points for virtual or tangible items. |
| **Transparency Hub** | Financial Governance | Public finance dashboard showing spending and budgets, and a voting system for stakeholders. |
| **AI Engine (ai\_engine)** | AI Infrastructure Management | Configuration and logging for all AI interactions (Gemini/OpenAI) including cost tracking and performance monitoring. |

-----

## Technology Stack

| Layer | Primary Technology | Key Dependencies & Tools |
| :--- | :--- | :--- |
| **Frontend** | **React** (Vite) | React Router DOM, TailwindCSS, `axios`, `lucide-react`. |
| **Backend** | **Django REST Framework** | `djangorestframework`, `djangorestframework_simplejwt`, `django-filter`, `corsheaders`. |
| **Database** | **PostgreSQL** | Used for relational data (users, classes, logs). |
| **AI** | **Google Gemini / OpenAI API** | Used for study personalization, sentiment analysis, and toxicity detection. |

-----

## Local Development Setup

To run the project locally, you need Python/Django for the backend and Node.js/Vite for the frontend.

### Prerequisites

  * Python (3.10+)
  * Node.js (18+)
  * PostgreSQL Database instance

### 1\. Backend Setup (`backend/`)

1.  **Navigate to the backend directory:**

    ```bash
    cd backend
    ```

2.  **Create and activate a Python virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # .\venv\Scripts\activate  # On Windows PowerShell
    ```

3.  **Install Python dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a file named **`.env`** inside the `backend/` directory to hold your database credentials and secret keys.

    ```env
    # .env
    SECRET_KEY=django-insecure-kgsf-s6+xrzfd=1ze&04n&jn-4jdw^@4t36%jnm3w$pv6mf42i
    DEBUG=True

    DB_NAME=skillnexus_db
    DB_USER=postgres
    DB_PASSWORD=1234567
    DB_HOST=localhost
    DB_PORT=5432

    # AI Service Key (Used by ai_engine and elibrary/utils)
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
    ```

5.  **Run Migrations:**

    ```bash
    python manage.py makemigrations 
    python manage.py migrate
    ```

6.  **Create a Superuser (Admin):**

    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the Django server:**

    ```bash
    python manage.py runserver
    ```

    The API will be available at `http://127.0.0.1:8000/`.

### 2\. Frontend Setup (`frontend/`)

1.  **Open a new terminal window or tab** and navigate to the frontend directory:

    ```bash
    cd frontend
    ```

2.  **Install Node dependencies:**

    ```bash
    npm install
    ```

3.  **Run the Vite development server:**

    ```bash
    npm run dev
    ```

    The frontend will typically open at `http://localhost:5173/`.

The frontend connects to the backend API defined in the environment variable `VITE_API_URL` (defaulting to `http://localhost:8000/api`).

-----

## Project Structure

The repository follows a standard monorepo structure with Django (for the backend) and React/Vite (for the frontend).

```
SkillXP-Nexus/
├── backend/                  # Django Backend Project
│   ├── SkillNexus/           # Main Django Project Config
│   ├── users/                # User Authentication and Profiles
│   ├── classroom/            # Learning Management System (LMS)
│   ├── elibrary/             # AI-Curated Learning Resources
│   ├── rewards/              # XP and Gamification Logic
│   ├── ai_engine/            # AI Configuration, Logging, and Auditing
│   ├── notifications/        # Centralized Alerts and Push Messages
│   ├── social/               # Community Forums and Messaging
│   ├── transparency/         # Financial and Governance Dashboard
│   ├── transport/            # GPS Tracking and Safety (Uber-Style)
│   └── manage.py
├── frontend/                 # React (Vite) Frontend Application
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── context/
│   │   └── services/         # API connection logic
└── README.md
```
