# TOODEEP
general insanity and goofiness

```
conda env create -f environment.yml
conda activate toodeep

python tourney/app.py
```

flask should log something about the localhost IP it's running on while the app is launching. The program takes in any valid scryfall query assuming your pc is beefy enough to hold every result in memory. Initial query may take a minute just so we don't get booted from scryfall's API.

TODO:
- add image prerendering to make the experience a lil smoother (buffer one or two matches ahead of time)
- make the buttons and text a bit bigger

