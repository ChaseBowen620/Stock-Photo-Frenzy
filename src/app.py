import os
import secrets
import string
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv
from .models import db, Lobby, LobbyParticipant
import qrcode
import io
import base64
import json
import random
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))

# Database configuration
database_url = os.getenv('DATABASE_URL')
if not database_url:
    # Default to SQLite for local development
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'stock_photo_frenzy.db')
    database_url = f'sqlite:///{db_path}'
elif database_url.startswith('postgres://'):
    # Handle Render's postgres:// URL format (needs postgresql://)
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Shutterstock API configuration
SHUTTERSTOCK_BASE_URL = os.getenv('SHUTTERSTOCK_BASE_URL', 'https://api.shutterstock.com/v2')
SHUTTERSTOCK_ACCESS_TOKEN = os.getenv('SHUTTERSTOCK_ACCESS_TOKEN', '')

# Popular search terms for variety
SEARCH_TERMS = [
    'nature', 'city', 'technology', 'business', 'people', 'food', 'travel',
    'architecture', 'abstract', 'landscape', 'portrait', 'lifestyle', 'sports',
    'animals', 'flowers', 'ocean', 'mountains', 'sunset', 'art', 'design'
]

# Player colors for Free-for-All mode
PLAYER_COLORS = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
    '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52BE80'
]

def generate_lobby_code():
    """Generate a short, unique lobby code"""
    characters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(secrets.choice(characters) for _ in range(6))
        # Check if code already exists
        if not Lobby.query.filter_by(id=code).first():
            return code

def generate_qr_code(data):
    """Generate QR code image as base64 string"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def extract_words(title):
    """Extract guessable words from title"""
    import re
    common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'under', 'over', 'around', 'near', 'far', 'here', 'there', 'where', 'when', 'why', 'how', 'what', 'who', 'which', 'that', 'this', 'these', 'those', 'some', 'any', 'all', 'both', 'each', 'every', 'other', 'another', 'such', 'same', 'different', 'new', 'old', 'good', 'bad', 'big', 'small', 'large', 'little', 'long', 'short', 'high', 'low', 'great', 'first', 'last', 'next', 'previous', 'main', 'major', 'minor', 'important', 'necessary', 'possible', 'available', 'present', 'current', 'recent', 'early', 'late', 'young', 'mature', 'fresh', 'clean', 'dirty', 'hot', 'cold', 'warm', 'cool', 'dry', 'wet', 'full', 'empty', 'open', 'closed', 'free', 'busy', 'ready', 'finished', 'complete', 'partial', 'total', 'whole', 'half', 'quarter', 'double', 'single', 'multiple', 'several', 'many', 'few', 'most', 'least', 'more', 'less', 'much', 'little', 'enough', 'too', 'very', 'quite', 'rather', 'pretty', 'fairly', 'almost', 'nearly', 'about', 'around', 'approximately', 'exactly', 'precisely', 'just', 'only', 'even', 'still', 'yet', 'already', 'soon', 'now', 'then', 'today', 'yesterday', 'tomorrow', 'always', 'never', 'sometimes', 'often', 'usually', 'rarely', 'hardly', 'barely', 'scarcely', 'extremely', 'highly', 'completely', 'totally', 'entirely', 'fully', 'partly', 'partially', 'mostly', 'mainly', 'primarily', 'especially', 'particularly', 'specifically', 'generally', 'normally', 'typically', 'commonly', 'frequently', 'regularly', 'occasionally', 'seldom', 'forever', 'permanently', 'temporarily', 'briefly', 'quickly', 'slowly', 'suddenly', 'gradually', 'immediately', 'instantly', 'eventually', 'finally', 'ultimately', 'initially', 'originally', 'previously', 'formerly', 'lately', 'presently', 'nowadays', 'tonight', 'whose', 'whom'}
    
    # Replace punctuation with spaces and split
    words = re.sub(r'[^\w\s]', ' ', title.lower())
    words = words.split()
    
    # Filter: length >= 3 and not common word
    words = [w for w in words if len(w) >= 3 and w not in common_words]
    
    return words

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/lobby', methods=['GET', 'POST'])
def lobby():
    """Lobby page for multiplayer game"""
    lobby_id = session.get('lobby_id')
    
    if request.method == 'POST':
        # Create a new lobby with mode and difficulty
        game_mode = request.form.get('game_mode', 'free-for-all')
        difficulty = request.form.get('difficulty', 'hard')
        
        lobby_code = generate_lobby_code()
        new_lobby = Lobby(
            id=lobby_code,
            status='waiting',
            game_mode=game_mode,
            difficulty=difficulty
        )
        db.session.add(new_lobby)
        db.session.commit()
        
        lobby_id = lobby_code
        session['lobby_id'] = lobby_id
        return redirect(url_for('lobby'))
    
    if not lobby_id:
        # Redirect to home if no lobby
        return redirect(url_for('index'))
    
    lobby_obj = Lobby.query.get(lobby_id)
    if not lobby_obj:
        session.pop('lobby_id', None)
        return redirect(url_for('lobby'))
    
    # Generate QR code for joining
    base_url = request.host_url.rstrip('/')
    join_url = f"{base_url}/join/{lobby_id}"
    qr_code = generate_qr_code(join_url)
    
    # Get mode description
    mode_descriptions = {
        'free-for-all': 'All players compete individually. Each player has a unique color!',
        'competitive': 'Two teams compete. 6 rounds alternating between red and blue teams.',
        'cooperative': 'All players work together for one shared score!'
    }
    
    return render_template('lobby.html', 
                         lobby=lobby_obj, 
                         qr_code=qr_code, 
                         join_url=join_url,
                         mode_description=mode_descriptions.get(lobby_obj.game_mode, ''))

@app.route('/join/<lobby_id>')
def join_lobby(lobby_id):
    """Join lobby page - for mobile users scanning QR code"""
    lobby_obj = Lobby.query.get(lobby_id)
    if not lobby_obj:
        return render_template('join_error.html', error="Lobby not found")
    
    if lobby_obj.status != 'waiting':
        return render_template('join_error.html', error="This lobby is no longer accepting players")
    
    return render_template('join_lobby.html', lobby=lobby_obj)

@app.route('/game')
def game():
    """Main game page"""
    lobby_id = request.args.get('lobby')
    is_mobile = request.args.get('mobile') == 'true' or request.user_agent.platform in ['iPhone', 'Android', 'Mobile']
    
    if lobby_id:
        # Multiplayer mode
        lobby = Lobby.query.get(lobby_id)
        if not lobby:
            return redirect(url_for('index'))
        
        if lobby.status == 'waiting':
            return redirect(url_for('lobby'))
        
        # Use mobile template for mobile devices in multiplayer
        if is_mobile:
            return render_template('game_mobile.html', 
                                 is_multiplayer=True,
                                 lobby_id=lobby_id)
        
        return render_template('game_host.html', 
                             is_multiplayer=True,
                             lobby_id=lobby_id)
    else:
        # Single player mode
        return render_template('game_single.html', is_multiplayer=False)

@app.route('/api/get-image', methods=['GET'])
def get_image():
    """Get a random image from Shutterstock API"""
    try:
        random_term = random.choice(SEARCH_TERMS)
        
        response = requests.get(
            f"{SHUTTERSTOCK_BASE_URL}/images/search",
            params={
                'query': random_term,
                'sort': 'random',
                'per_page': 1,
                'view': 'full'
            },
            headers={
                'Authorization': f'Bearer {SHUTTERSTOCK_ACCESS_TOKEN}',
                'Content-Type': 'application/json'
            }
        )
        
        if not response.ok:
            return jsonify({'error': f'API request failed: {response.status_code}'}), 500
        
        data = response.json()
        
        if not data.get('data') or len(data['data']) == 0:
            return jsonify({'error': 'No images found'}), 404
        
        image = data['data'][0]
        
        # Get best image URL
        image_url = None
        asset_sizes = ['huge', 'large', 'medium', 'small', 'preview']
        for size in asset_sizes:
            if image.get('assets', {}).get(size, {}).get('url'):
                image_url = image['assets'][size]['url']
                break
        
        if not image_url:
            return jsonify({'error': 'No suitable image URL found'}), 404
        
        # Extract words from title
        title = image.get('description', 'Beautiful Stock Photo')
        title_words = extract_words(title)
        
        # For easy mode, select 3 random words to hide
        difficulty = request.args.get('difficulty', 'hard')
        easy_mode_hidden_words = []
        if difficulty == 'easy' and len(title_words) >= 3:
            easy_mode_hidden_words = random.sample(title_words, min(3, len(title_words)))
        
        return jsonify({
            'success': True,
            'image': {
                'id': image.get('id'),
                'url': image_url,
                'title': title,
                'title_words': title_words,
                'easy_mode_hidden_words': easy_mode_hidden_words,
                'contributor': image.get('contributor', {}).get('display_name', 'Unknown')
            }
        })
    
    except Exception as e:
        print(f'Error getting image: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/lobby/<lobby_id>/status')
def lobby_status(lobby_id):
    """Get lobby status and participants"""
    lobby = Lobby.query.get(lobby_id)
    if not lobby:
        return jsonify({'error': 'Lobby not found'}), 404
    
    participants = [p.to_dict() for p in lobby.participants]
    
    return jsonify({
        'lobby': lobby.to_dict(),
        'participants': participants
    })

@app.route('/api/lobby/<lobby_id>/join', methods=['POST'])
def api_join_lobby(lobby_id):
    """API endpoint to join a lobby"""
    lobby = Lobby.query.get(lobby_id)
    if not lobby:
        return jsonify({'error': 'Lobby not found'}), 404
    
    if lobby.status != 'waiting':
        return jsonify({'error': 'Lobby is no longer accepting players'}), 400
    
    # Get player name from request
    data = request.json
    player_name = data.get('player_name', '').strip()
    if not player_name:
        return jsonify({'error': 'Player name is required'}), 400
    
    # Generate a unique session ID for this player
    player_id = secrets.token_hex(8)
    session[f'player_id_{lobby_id}'] = player_id
    session[f'player_name_{lobby_id}'] = player_name
    
    # Assign color for Free-for-All mode or Competitive mode (for round 5 highlighting)
    player_color = None
    if lobby.game_mode == 'free-for-all' or lobby.game_mode == 'competitive':
        existing_colors = [p.player_color for p in lobby.participants if p.player_color]
        available_colors = [c for c in PLAYER_COLORS if c not in existing_colors]
        player_color = available_colors[0] if available_colors else PLAYER_COLORS[len(lobby.participants) % len(PLAYER_COLORS)]
    
    # Add participant
    participant = LobbyParticipant(
        lobby_id=lobby_id,
        player_name=player_name,
        player_color=player_color
    )
    db.session.add(participant)
    db.session.commit()
    
    return jsonify({'success': True, 'participant': participant.to_dict(), 'player_id': player_id})

@app.route('/api/lobby/<lobby_id>/start', methods=['POST'])
def start_lobby_game(lobby_id):
    """Start the game for a lobby"""
    lobby = Lobby.query.get(lobby_id)
    
    if not lobby:
        return jsonify({'error': 'Lobby not found'}), 404
    
    if lobby.status != 'waiting':
        return jsonify({'error': 'Game has already started'}), 400
    
    participants = lobby.participants
    if len(participants) < 1:
        return jsonify({'error': 'Need at least one participant to start'}), 400
    
    # For Competitive mode, select team captains
    if lobby.game_mode == 'competitive':
        if len(participants) < 2:
            return jsonify({'error': 'Need at least 2 participants for Competitive mode'}), 400
        
        # Randomly select two captains
        captains = random.sample(participants, 2)
        captains[0].is_captain = True
        captains[0].team = 'red'
        captains[1].is_captain = True
        captains[1].team = 'blue'
        
        # Assign other players to teams (alternating)
        other_players = [p for p in participants if not p.is_captain]
        for i, player in enumerate(other_players):
            player.team = 'red' if i % 2 == 0 else 'blue'
        
        lobby.team_captains = json.dumps([c.player_name for c in captains])
        lobby.active_team = 'red'  # Start with red team
    
    # Start the game
    from datetime import datetime
    lobby.status = 'active'
    lobby.started_at = datetime.utcnow()
    lobby.current_round = 0
    lobby.revealed_words = json.dumps([])
    lobby.word_owners = json.dumps({})
    lobby.shared_score = 0
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'lobby': lobby.to_dict()
    })

@app.route('/api/lobby/<lobby_id>/submit-word', methods=['POST'])
def submit_word(lobby_id):
    """Submit a word guess from a participant"""
    lobby = Lobby.query.get(lobby_id)
    if not lobby:
        return jsonify({'error': 'Lobby not found'}), 404
    
    if lobby.status != 'active':
        return jsonify({'error': 'Game is not active'}), 400
    
    data = request.json
    player_name = data.get('player_name')
    word = data.get('word', '').strip().lower()
    
    if not word or len(word) < 3:
        return jsonify({'error': 'Word must be at least 3 characters'}), 400
    
    # Find participant
    participant = LobbyParticipant.query.filter_by(lobby_id=lobby_id, player_name=player_name).first()
    if not participant:
        return jsonify({'error': 'Participant not found'}), 404
    
    # For Competitive mode, check if player's team is active (except round 5)
    if lobby.game_mode == 'competitive':
        # Round 5 (index 4, 0-indexed) is free-for-all for both teams
        # But still only captains can submit
        if not participant.is_captain:
            return jsonify({'error': 'Only team captains can submit words'}), 400
        
        # For rounds 1-4, check if it's the player's team's turn
        if lobby.current_round < 4:
            if participant.team != lobby.active_team:
                return jsonify({'error': 'It is not your team\'s turn'}), 400
        # Round 5: both teams can play (no team check needed)
    
    # Get current image data
    if not lobby.current_image_data:
        return jsonify({'error': 'No image loaded'}), 400
    
    image_data = json.loads(lobby.current_image_data)
    title_words = image_data.get('title_words', [])
    revealed_words = json.loads(lobby.revealed_words) if lobby.revealed_words else []
    word_owners = json.loads(lobby.word_owners) if lobby.word_owners else {}
    
    # Check if word is in title
    found_words = [w for w in title_words if w == word]
    is_correct = len(found_words) > 0
    
    # Get guessed words for this participant
    guessed_words = json.loads(participant.guessed_words) if participant.guessed_words else []
    
    if word in guessed_words:
        return jsonify({'error': 'You already guessed this word'}), 400
    
    # Add to guessed words
    guessed_words.append(word)
    participant.guessed_words = json.dumps(guessed_words)
    
    if is_correct:
        # Add to revealed words if not already revealed
        if word not in revealed_words:
            revealed_words.append(word)
            lobby.revealed_words = json.dumps(revealed_words)
            
            # For Free-for-All, track who found each word
            if lobby.game_mode == 'free-for-all':
                word_owners[word] = player_name
                lobby.word_owners = json.dumps(word_owners)
        
        # Award points based on mode
        points = len(found_words) * 10
        
        if lobby.game_mode == 'cooperative':
            # Add to shared score
            lobby.shared_score += points
            if len(revealed_words) == len(title_words):
                lobby.shared_score += 100  # Completion bonus
        elif lobby.game_mode == 'competitive' and lobby.current_round >= 4:
            # Round 5: Free-for-all, track word owners for highlighting
            if word not in word_owners:
                word_owners[word] = player_name
                lobby.word_owners = json.dumps(word_owners)
            # Individual scoring
            participant.score += points
            if len(revealed_words) == len(title_words):
                participant.score += 100  # Completion bonus
        else:
            # Individual scoring (Free-for-All or Competitive rounds 1-4)
            if lobby.game_mode == 'free-for-all':
                # Track word owners for highlighting
                if word not in word_owners:
                    word_owners[word] = player_name
                    lobby.word_owners = json.dumps(word_owners)
            participant.score += points
            if len(revealed_words) == len(title_words):
                participant.score += 100  # Completion bonus
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'is_correct': is_correct,
        'points': len(found_words) * 10 if is_correct else 0,
        'revealed_words': revealed_words,
        'word_owners': word_owners if lobby.game_mode == 'free-for-all' else {},
        'score': participant.score if lobby.game_mode != 'cooperative' else lobby.shared_score,
        'player_color': participant.player_color if lobby.game_mode == 'free-for-all' else None
    })

@app.route('/api/lobby/<lobby_id>/next-round', methods=['POST'])
def next_round(lobby_id):
    """Move to next round (host only)"""
    lobby = Lobby.query.get(lobby_id)
    if not lobby:
        return jsonify({'error': 'Lobby not found'}), 404
    
    data = request.json or {}
    
    # If image_data is provided, store it (for starting a round)
    if 'image_data' in data:
        lobby.current_image_data = json.dumps(data['image_data'])
        lobby.revealed_words = json.dumps([])
        lobby.word_owners = json.dumps({})
        
        # Reset participant guessed words
        for participant in lobby.participants:
            participant.guessed_words = json.dumps([])
        
        db.session.commit()
        return jsonify({
            'success': True,
            'current_round': lobby.current_round,
            'game_finished': False
        })
    
    # Determine max rounds based on mode
    max_rounds = 5  # All modes use 5 rounds now
    
    # Check if game is finished
    if lobby.current_round >= max_rounds - 1:  # 0-indexed
        lobby.status = 'finished'
        db.session.commit()
        return jsonify({
            'success': True,
            'game_finished': True,
            'final_scores': [p.to_dict() for p in lobby.participants] if lobby.game_mode != 'cooperative' else {'shared_score': lobby.shared_score}
        })
    
    # Move to next round
    lobby.current_round += 1
    lobby.revealed_words = json.dumps([])
    lobby.word_owners = json.dumps({})
    lobby.current_image_data = None
    
    # For Competitive mode, switch active team
    # Round 1 (index 0): red, Round 2 (index 1): blue, Round 3 (index 2): red, Round 4 (index 3): blue, Round 5 (index 4): both
    if lobby.game_mode == 'competitive':
        if lobby.current_round < 4:
            # Rounds 1-4: alternate between red and blue
            # Round 1 (index 0): red (set at start)
            # Round 2 (index 1): blue
            # Round 3 (index 2): red
            # Round 4 (index 3): blue
            lobby.active_team = 'blue' if lobby.active_team == 'red' else 'red'
        elif lobby.current_round == 4:
            # Round 5 (index 4): Free-for-all, both teams can play
            lobby.active_team = None
    
    # Reset participant guessed words
    for participant in lobby.participants:
        participant.guessed_words = json.dumps([])
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'current_round': lobby.current_round,
        'game_finished': False,
        'active_team': lobby.active_team if (lobby.game_mode == 'competitive' and lobby.current_round < 4) else None,
        'is_free_for_all': lobby.game_mode == 'competitive' and lobby.current_round == 4
    })

@app.route('/api/lobby/<lobby_id>/leaderboard')
def get_leaderboard(lobby_id):
    """Get current leaderboard"""
    participants = LobbyParticipant.query.filter_by(lobby_id=lobby_id).order_by(
        LobbyParticipant.score.desc()
    ).all()
    
    leaderboard = [p.to_dict() for p in participants]
    return jsonify({'leaderboard': leaderboard})

@app.route('/results')
def results():
    """Display game results"""
    lobby_id = request.args.get('lobby')
    
    if lobby_id:
        # Multiplayer results
        lobby = Lobby.query.get(lobby_id)
        if not lobby:
            return redirect(url_for('index'))
        
        participants = LobbyParticipant.query.filter_by(lobby_id=lobby_id).order_by(
            LobbyParticipant.score.desc()
        ).all()
        
        leaderboard = [p.to_dict() for p in participants]
        max_rounds = 5  # All modes use 5 rounds
        
        return render_template('results.html', 
                             is_multiplayer=True, 
                             lobby_id=lobby_id, 
                             leaderboard=leaderboard,
                             game_mode=lobby.game_mode,
                             shared_score=lobby.shared_score,
                             total_rounds=max_rounds)
    else:
        # Single player results
        final_score = session.get('final_score', 0)
        return render_template('results.html', 
                             is_multiplayer=False, 
                             final_score=final_score,
                             total_rounds=5)

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

