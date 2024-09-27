from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
import math

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tournament.db'
db = SQLAlchemy(app)

# Model for Player
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

# Model for Match
class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player1_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    player2_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    winner_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    round_number = db.Column(db.Integer, nullable=False)

@app.route('/')
def index():
    # players = Player.query.all()
    # return render_template('bracket.html', players=players)
    return render_template('play.html')

# Create a tournament and generate initial matches
@app.route('/create_tournament', methods=['POST'])
def create_tournament():
    players = Player.query.all()
    num_players = len(players)
    num_rounds = math.ceil(math.log2(num_players))
    
    # Pair up players for the first round
    matches = []
    for i in range(0, num_players, 2):
        player1 = players[i]
        player2 = players[i+1] if i+1 < num_players else None  # Handle bye rounds
        match = Match(player1_id=player1.id, player2_id=player2.id if player2 else None, round_number=1)
        matches.append(match)
    
    db.session.add_all(matches)
    db.session.commit()
    
    return redirect(url_for('view_bracket'))

# View bracket
@app.route('/bracket')
def view_bracket():
    matches = Match.query.order_by(Match.round_number).all()
    return render_template('bracket.html', matches=matches)

# Report a winner
@app.route('/report_winner/<int:match_id>', methods=['POST'])
def report_winner(match_id):
    match = Match.query.get(match_id)
    winner_id = request.form['winner_id']
    match.winner_id = winner_id
    
    db.session.commit()
    
    # Handle progression to the next round
    next_round = match.round_number + 1
    # Find or create the next round match for the winner
    return redirect(url_for('view_bracket'))

# Add a new player to the tournament
@app.route('/add_player', methods=['POST'])
def add_player():
    player_name = request.form['name']
    new_player = Player(name=player_name)
    db.session.add(new_player)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

    app.add_player()