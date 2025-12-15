from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Lobby(db.Model):
    """Game lobby for multiplayer stock photo game"""
    __tablename__ = 'lobbies'
    
    id = db.Column(db.String(10), primary_key=True)  # Short code like "ABC123"
    status = db.Column(db.String(20), default='waiting')  # waiting, active, finished
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    current_round = db.Column(db.Integer, default=0)  # Current round
    current_image_data = db.Column(db.Text)  # JSON of current image info
    revealed_words = db.Column(db.Text)  # JSON array of revealed words
    word_owners = db.Column(db.Text)  # JSON dict: word -> player_name (for Free-for-All colors)
    game_mode = db.Column(db.String(20), default='free-for-all')  # free-for-all, competitive, cooperative
    difficulty = db.Column(db.String(10), default='hard')  # easy, hard
    team_captains = db.Column(db.Text)  # JSON array of two player names for competitive mode
    active_team = db.Column(db.String(10), nullable=True)  # 'red' or 'blue' for competitive mode
    shared_score = db.Column(db.Integer, default=0)  # For cooperative mode
    game_phrase = db.Column(db.String(100), nullable=True)  # Phrase for all rounds (optional)
    red_team_phrase = db.Column(db.String(100), nullable=True)  # Deprecated - kept for backwards compatibility
    blue_team_phrase = db.Column(db.String(100), nullable=True)  # Deprecated - kept for backwards compatibility
    round5_team = db.Column(db.String(10), nullable=True)  # Deprecated - kept for backwards compatibility
    
    # Relationships
    participants = db.relationship('LobbyParticipant', backref='lobby', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        image_data = None
        if self.current_image_data:
            try:
                image_data = json.loads(self.current_image_data)
            except:
                pass
        revealed = []
        if self.revealed_words:
            try:
                revealed = json.loads(self.revealed_words)
            except:
                pass
        word_owners_dict = {}
        if self.word_owners:
            try:
                word_owners_dict = json.loads(self.word_owners)
            except:
                pass
        
        team_captains_list = []
        if self.team_captains:
            try:
                team_captains_list = json.loads(self.team_captains)
            except:
                pass
        
        return {
            'id': self.id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'participant_count': len(self.participants),
            'current_round': self.current_round,
            'current_image_data': image_data,
            'revealed_words': revealed,
            'word_owners': word_owners_dict,
            'game_mode': self.game_mode,
            'difficulty': self.difficulty,
            'team_captains': team_captains_list,
            'active_team': self.active_team,
            'shared_score': self.shared_score,
            'game_phrase': self.game_phrase,
            'red_team_phrase': self.red_team_phrase,
            'blue_team_phrase': self.blue_team_phrase,
            'round5_team': self.round5_team
        }


class LobbyParticipant(db.Model):
    """Participants in a lobby"""
    __tablename__ = 'lobby_participants'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lobby_id = db.Column(db.String(10), db.ForeignKey('lobbies.id'), nullable=False, index=True)
    player_name = db.Column(db.String(100), nullable=False)  # Display name for the game
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    score = db.Column(db.Integer, default=0)  # Total score across all rounds
    guessed_words = db.Column(db.Text)  # JSON array of words guessed this round
    player_color = db.Column(db.String(20), nullable=True)  # Color for Free-for-All mode
    team = db.Column(db.String(10), nullable=True)  # 'red' or 'blue' for Competitive mode
    is_captain = db.Column(db.Boolean, default=False)  # True if team captain in Competitive mode
    
    def to_dict(self):
        guessed = []
        if self.guessed_words:
            try:
                guessed = json.loads(self.guessed_words)
            except:
                pass
        return {
            'id': self.id,
            'lobby_id': self.lobby_id,
            'player_name': self.player_name,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'score': self.score,
            'guessed_words': guessed,
            'player_color': self.player_color,
            'team': self.team,
            'is_captain': self.is_captain
        }

