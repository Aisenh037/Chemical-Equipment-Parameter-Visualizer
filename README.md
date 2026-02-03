# Chemical Equipment Parameter Visualizer (EquiViz Pro)

A hybrid Web and Desktop application for visualizing and analyzing chemical equipment data.

## Features
- **CSV Data Upload**: Upload equipment parameters (Name, Type, Flowrate, Pressure, Temperature).
- **Automated Analysis**: Backend calculates averages, total counts, and type distribution using Pandas.
- **Dynamic Visualization**: 
  - **Web**: Interactive Bar and Pie charts using Chart.js.
  - **Desktop**: Data plots using Matplotlib within PyQt5.
- **History Management**: Store metadata for the last 5 uploaded datasets.
- **PDF Report Generation**: Download detailed analysis reports as PDFs.
- **Security**: Basic Authentication for API access.

## Tech Stack
- **Backend**: Django, Django REST Framework, Pandas, ReportLab.
- **Web Frontend**: React.js, Vite, Chart.js, Axios.
- **Desktop Frontend**: PyQt5, Matplotlib, Requests.
- **Database**: SQLite.

## Project Structure
```
IITB/
├── backend/            # Django API
├── web-frontend/       # React application
├── desktop-frontend/   # PyQt5 application
├── data/               # Sample CSV files
└── README.md
```

## Setup Instructions

### 1. Backend Setup
1. Navigate to the backend directory: `cd backend`
2. Activate the virtual environment: `.\venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt` (or manually if not provided)
4. Run migrations: `python manage.py migrate`
5. Start the server: `python manage.py runserver`
   - *Default credentials: admin / password123*

### 2. Web Frontend Setup
1. Navigate to `web-frontend`
2. Install dependencies: `npm install`
3. Start dev server: `npm run dev`

### 3. Desktop Frontend Setup
1. Navigate to `desktop-frontend`
2. Ensure you have the backend dependencies installed (PyQt5, matplotlib, requests)
3. Run the application: `python main.py`

## Sample Data
Use the provided `data/sample_equipment_data.csv` for initial testing.
