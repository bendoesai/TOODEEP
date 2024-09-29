from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import requests
import time
import urllib

app = Flask(__name__)
app.secret_key = 'abc123'

@app.route("/", methods=["GET", "POST"])
def scryfall_query():
    
    # Define the base URL for Scryfall's API
    base_url = 'https://api.scryfall.com/cards/search'
    
    if request.method == "POST":
        query = request.form.get("query")
        
        # Define the query
        #query = '%28plains+OR+island+OR+swamp+OR+mountain+OR+forest+OR+wastes%29+t%3Abasic+t%3Aland&unique=art&as=grid&order=name'  # URL-encoded query
        query = urllib.parse.quote_plus(query)
        options = request.form.get('options')
        print(f'{query}&unique={options}')

        # Make the request
        response = requests.get(f'{base_url}?q={query}&unique={options}')

        # Check if the request was successful
        if response.status_code == 200:
            print("SUCCESSFUL QUERY")
            data = response.json()
            print(data["object"], data["total_cards"], data["has_more"])
            
            entrants = data["total_cards"]

            # Process the data (for example, print card names)
            while data['has_more'] == True:
                response = requests.get(data['next_page'])
                data = response.json()
                for card in data['data']:
                    try:
                        print(card['image_uris']['large'])
                    except:
                        continue
                print(data["object"], data["total_cards"], data["has_more"])
                time.sleep(0.1) #so scryfall doesn't yell at me (i would cry)
        else:
            print(f'Error: {response.status_code}')
            #Error Handling
            return render_template("scryfall_search.html")

        return redirect(url_for("tournament"))

    return render_template("scryfall_search.html")

@app.route("/tournament", methods=["GET", "POST"])
def tournament():
    if request.method == "POST":
        # Check which button was clicked by examining the form data
        if request.form.get("BACK"):
            print("BACK button clicked")
            # Process the "BACK" button click here

        elif request.form.get("EVYN"):
            print("EVYN BUTTON clicked")
            session['kinkadian'] = session.get('kinkadian', 0) + 1
            # Process the "EVYN" click here

        elif request.form.get("card"):
            # Handle image buttons by checking the request form data
            print(f"{request.form.get("card")} button clicked")

        elif request.form.get("RESET"):
            #cleanup tasks
            print("RESETTING TOURNAMENT")
            session.clear()
            return redirect(url_for("scryfall_query"))
        
        else:
            print("unknown POST")

        return redirect(url_for("tournament"))  # Redirect to avoid resubmission

    kinkadian = session.get('kinkadian', 0)

    return render_template("play.html", kinkadian=kinkadian, card1=card1, card2=card2)  # Render your HTML template

class SingleElimTournament:
    def __init__(entrants=[]):
        self.player_list = entrants

    def get_next_match():
        return card1, card2

    def record_winner():
        pass

    def undo_round():
        pass


if __name__ == "__main__":
    app.run(debug=True)