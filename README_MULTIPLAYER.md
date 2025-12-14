# Stock Photo Frenzy - Multiplayer Mode

This document describes the multiplayer functionality added to Stock Photo Frenzy.

## Features

### Multiplayer Mode
- **Lobby System**: Create a lobby with a unique 6-character code
- **QR Code**: Share a QR code for easy mobile joining
- **Host Screen**: Host sees the image and leaderboard (no submission bar)
- **Mobile Interface**: Participants join on their phones and submit words
- **Real-time Updates**: Words revealed in real-time as players guess correctly
- **5 Rounds**: Both single player and multiplayer modes are capped at 5 rounds
- **Final Scores**: Leaderboard shown after all rounds complete

### Single Player Mode
- Still available with the same gameplay
- Now capped at 5 rounds
- Final score displayed after completion

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file (see `.env.example`):
```env
SECRET_KEY=your-secret-key-here
SHUTTERSTOCK_ACCESS_TOKEN=your-shutterstock-access-token
```

3. Run the application:
```bash
python -m src.app
```

Or with Flask:
```bash
export FLASK_APP=src.app
flask run
```

## How to Play Multiplayer

1. **Host**: Click "Multiplayer" on the home page
2. **Lobby**: Share the QR code or lobby code with players
3. **Players**: Scan QR code or visit join URL on their phones
4. **Start**: Host clicks "Start Game" when ready
5. **Play**: 
   - Host sees the image and leaderboard
   - Players submit words on their phones
   - Words reveal in real-time
6. **Next Round**: Host clicks "Next Round" after each round
7. **Results**: Final leaderboard shown after 5 rounds

## Project Structure

```
stock-photo-frenzy/
├── src/
│   ├── __init__.py
│   ├── app.py          # Flask application
│   └── models.py       # Database models
├── templates/
│   ├── base.html
│   ├── index.html      # Home page
│   ├── lobby.html      # Lobby with QR code
│   ├── join_lobby.html # Join page
│   ├── game_single.html # Single player game
│   ├── game_host.html  # Host screen
│   ├── game_mobile.html # Mobile participant screen
│   └── results.html    # Final results
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── requirements.txt
└── README_MULTIPLAYER.md
```

## API Endpoints

- `GET /` - Home page
- `GET /lobby` - Create/join lobby
- `GET /join/<lobby_id>` - Join lobby page
- `GET /game` - Game page (single or multiplayer)
- `GET /results` - Results page
- `GET /api/get-image` - Get random image from Shutterstock
- `GET /api/lobby/<lobby_id>/status` - Get lobby status
- `POST /api/lobby/<lobby_id>/join` - Join lobby
- `POST /api/lobby/<lobby_id>/start` - Start game
- `POST /api/lobby/<lobby_id>/submit-word` - Submit word guess
- `POST /api/lobby/<lobby_id>/next-round` - Move to next round
- `GET /api/lobby/<lobby_id>/leaderboard` - Get leaderboard

## Database

The app uses SQLite by default (or PostgreSQL if `DATABASE_URL` is set). Tables:
- `lobbies` - Game lobbies
- `lobby_participants` - Players in each lobby

