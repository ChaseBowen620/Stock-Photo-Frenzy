# Quick Start Guide

## How to Run the Game

Since the game is now a Flask application, you need to run it as a server instead of just opening the HTML file.

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set Up Environment Variables

Create a `.env` file in the `stock-photo-frenzy` folder with:

```env
SECRET_KEY=your-secret-key-here
SHUTTERSTOCK_ACCESS_TOKEN=your-shutterstock-access-token
```

### Step 3: Run the Application

**Option A: Using the run script**
```bash
python run.py
```

**Option B: Using Flask directly**
```bash
python -m src.app
```

**Option C: Using Flask command**
```bash
export FLASK_APP=src.app
flask run
```

### Step 4: Access the Game

Open your web browser and go to:
```
http://localhost:5000
```

That's it! The game should now be running.

## Notes

- The app will create a SQLite database file (`stock_photo_frenzy.db`) automatically on first run
- Make sure you have a valid Shutterstock API access token in your `.env` file
- The app runs on port 5000 by default

