import random
import requests
import time
import urllib

from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'abc123'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route("/", methods=["GET", "POST"])
def scryfall_query():
    base_url = 'https://api.scryfall.com/cards/search'

    if request.method == "POST":
        query = request.form.get("query")
        query = urllib.parse.quote_plus(query)
        options = request.form.get('options')

        card_list = []
        response = requests.get(f'{base_url}?q={query}&unique={options}')

        if response.status_code == 200:
            data = response.json()
            session['num_matches'] = data['total_cards']
            print(data['total_cards'])
            # Initial card processing
            for card in data['data']:
                try:
                    print(card['image_uris']['large'])
                    card_list.append(card['image_uris']['large'])
                except:
                    continue
            time.sleep(0.1)

            # Process more pages if any
            while data['has_more']:
                response = requests.get(data['next_page'])
                data = response.json()
                for card in data['data']:
                    try:
                        print(card['image_uris']['large'])
                        card_list.append(card['image_uris']['large'])
                    except:
                        continue
                time.sleep(0.1)

            random.shuffle(card_list)
            session['bracket'] = SingleElimTournament(card_list).to_dict()
            session['kinkadian'] = 0
        else:
            return render_template("scryfall_search.html")

        return redirect(url_for("tournament"))

    return render_template("scryfall_search.html")

@app.route("/tournament", methods=["GET", "POST"])
def tournament():
    if 'bracket' not in session:
        return redirect(url_for('scryfall_query'))

    bracket = SingleElimTournament.from_dict(session['bracket'])

    if request.method == "POST":
        if request.form.get("BACK"):
            bracket.undo_round()

        elif request.form.get("EVYN"):
            session['kinkadian'] += 1

        elif request.form.get("card"):
            next_match, is_over = bracket.record_winner(request.form.get("card"))

            if is_over:
                session['bracket'] = bracket.to_dict()  # Save the updated tournament state
                return redirect(url_for('winner'))

        elif request.form.get("RESET"):
            session.clear()
            return redirect(url_for("scryfall_query"))
        
        session['bracket'] = bracket.to_dict()
        return redirect(url_for("tournament"))

    card1image, card2image = bracket.next_match
    if card1image is None or card2image is None:
        return redirect(url_for('winner'))

    return render_template("play.html", kinkadian=session['kinkadian'], card1image=card1image, card2image=card2image)

@app.route("/winner", methods=["GET", "POST"])
def winner():
    winner = session['winner']
    if request.method == "POST":
        if request.form.get("RESET"):
            session.clear()
            return redirect(url_for("scryfall_query"))
        else:
            print("unknown POST")

        return redirect(url_for("winner"))

    return render_template("winner.html", winner=winner)

class SingleElimTournament:
    def __init__(self, entrants=None):
        if entrants is None:
            entrants = []
        self.player_list = entrants
        self.winner_list = []
        self.is_over = False
        self.last_match = []
        self.next_match = (None, None) if len(entrants) < 2 else (entrants[0], entrants[1])

    def record_winner(self, winner):
        self.last_match = [self.player_list[0], self.player_list[1]]
        if winner == 'card1':
            self.winner_list.append(self.player_list.pop(0))
            self.player_list.pop(0)
        elif winner == 'card2':
            self.winner_list.append(self.player_list.pop(1))
            self.player_list.pop(0)
        else:
            print("unknown winner")

        if len(self.player_list) == 1:
            self.winner_list.append(self.player_list.pop(0))

        if len(self.player_list) == 0:
            self.player_list = self.winner_list
            self.winner_list = []

        if len(self.player_list) == 1 and len(self.winner_list) == 0:
            self.is_over = True
            session['winner'] = self.player_list[0]

        self.next_match = (None, None) if len(self.player_list) < 2 else (self.player_list[0], self.player_list[1])

        return self.next_match, self.is_over

    def undo_round(self):
        self.player_list.insert(0, self.last_match[0])
        self.player_list.insert(1, self.last_match[1])
        if len(self.winner_list) > 0:
            self.winner_list.pop()

    def to_dict(self):
        return {
            'player_list': self.player_list,
            'winner_list': self.winner_list,
            'is_over': self.is_over,
            'last_match': self.last_match
        }

    @classmethod
    def from_dict(cls, data):
        tournament = cls(data['player_list'])
        tournament.winner_list = data['winner_list']
        tournament.is_over = data['is_over']
        tournament.last_match = data['last_match']
        return tournament

if __name__ == "__main__":
    app.run(debug=True)