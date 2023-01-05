from os import close
import random
import re
import tkinter as tk
from tkinter import *
import tkinter.ttk as ttk
from ttkthemes import ThemedStyle  
import json
import webbrowser

K = 27
pairList = []
mainGenres = {}
usedGenres = {}
genre_json = "main_genres_parameters_all.json"
results_json = "main_genres_parameters_result.json"
checked_list_json = "used_genres.json"
spotify_url = "https://open.spotify.com/search/"


root = tk.Tk() 
root.title("Music Genres")
root.geometry("700x700")
root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file='music_icon.png'))


style = ThemedStyle(root)
s = ttk.Style()
style.theme_use('breeze')


root.configure(bg=style.lookup('TLabel', 'background'))

# Returns json file
def readJson(source):
    try:
        with open(source, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"read JSON error: {e}")
        return
    
# Dumps data to preferred json file
def writeJson(source, json_data):
    try:
        with open(source, "w") as file:
            json.dump(json_data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Write JSON error: {e}")

class Genre:
    def __init__(self, name):
        self.name = name
        try:
            self.list = readJson(checked_list_json)
            self.result = readJson(results_json)
        except Exception as e:
            print(f"results json error: {e}")
            self.list = {}
            self.result = {}

    def getRank(self):
        return self.list[f'{self.name}']['Rank']

    def setRank(self, newRank):
        self.list[f'{self.name}']['Rank'] = newRank
        writeJson(checked_list_json, self.list)
    
    def addToResults(self):
        self.result[self.name] = self.list[self.name]
        writeJson(results_json, self.result)


genre1 = Genre(None)
genre2 = Genre(None)

# Returns new propability for change to win using formula and rank of two genres.
def calculatePropability(r_one, r_two):
    return (1.0 * 1.0 / (1.0 + pow(10, (r_one - r_two) / 400)))

# Calculate propability when A wins
def optionAPropability():
    Ra = genre1.getRank()
    Rb = genre2.getRank()
    Pa = (1.0 * 1.0 / (1.0 + pow(10, (Rb - Ra) / 400)))
    Pb = (1.0 * 1.0 / (1.0 + pow(10, (Ra - Rb) / 400)))
    Ra = Ra + K * (1 - Pa)
    Rb = Rb + K * (0 - Pb) 
    genre1.setRank(Ra)
    genre2.setRank(Rb)
    genre1.addToResults()
    # update buttons and list view
    update()

# Calculate propability when B wins
def optionBPropability():
    Ra = genre1.getRank()
    Rb = genre2.getRank()
    Pa = (1.0 * 1.0 / (1.0 + pow(10, (Ra - Rb) / 400)))
    Pb = (1.0 * 1.0 / (1.0 + pow(10, (Rb - Ra) / 400)))
    Ra = Ra + K * (0 - Pa)
    Rb = Rb + K * (1 - Pb)
    genre1.setRank(Ra)
    genre2.setRank(Rb)
    genre2.addToResults()
    # update buttons and list view
    update()

# If user presses skip button
def skip():
    Ra = genre1.getRank()
    Rb = genre2.getRank()
    Pa = (1.0 * 1.0 / (1.0 + pow(10, (Ra - Rb) / 400)))
    Pb = (1.0 * 1.0 / (1.0 + pow(10, (Rb - Ra) / 400)))
    Ra = Ra + K * (0 - Pa)
    Rb = Rb + K * (0 - Pb)
    genre1.setRank(Ra)
    genre2.setRank(Rb)
    pickAPair()

# Update list and add results to genreList
def updateListbox():
    genresForList = readJson(results_json)
    if genresForList != None:
        if len(genresForList) > 0:
            # sort results based on rank using lambda
            genres = sorted(genresForList, key=lambda x: (genresForList[x]['Rank']), reverse=True)
            genreList.delete(0, END)
            # insert to genreList
            for i, key in enumerate(list(genres)):
                genreList.insert(i, f"{i+1}. { key }")

# Pick random pair of gneres
def pickAPair():
    global pairList, genre1, genre2

    mainGenres = readJson(checked_list_json)
    randKey1 = random.choice(list(mainGenres))
    randKey2 = random.choice(list(mainGenres))
    randKey1Former= None
    randKey2Former = None
    sum = 0
    averageRank = 1400

    for i, key in enumerate(list(mainGenres)):
        sum += mainGenres[key]['Rank']
    averageRank = sum/len(list(mainGenres))

    while (True):
        if (randKey1 == randKey2 or randKey1 == randKey1Former or 
        randKey2 == randKey2Former or randKey1 == randKey2Former or 
        randKey2 == randKey1Former):
            # Delete selected genres if rank is 3 points under average
            if averageRank - 3 < mainGenres[randKey1]['Rank']: 
                print(f"Deleting {randKey1}")
                del mainGenres[randKey1]

            elif averageRank - 3 < mainGenres[randKey2]['Rank']:
                print(print(f"Deleting {randKey2}"))
                del mainGenres[randKey2]

            writeJson(checked_list_json, mainGenres)
            randKey1 = random.choice(list(mainGenres))
            randKey2 = random.choice(list(mainGenres))

        else: break

    pairList.clear()
    pairList.append(randKey1)
    pairList.append(randKey2)
    genre1 = Genre(pairList[0])
    genre2 = Genre(pairList[1]) 
    choose_a.config(text=randKey1)
    choose_b.config(text=randKey2)
    randKey1Former = randKey1
    randKey2Former = randKey1


def update():
    updateListbox()
    pickAPair()


def closeWindow():
    root.destroy()

# search genre from Spotify using webbrowser library
def searchFromSpotify():
    # replace white space with %20
    try:
        search = genreList.get(genreList.curselection())
        search = re.sub(r'([1-9][0-9]?|100). ', '', search)
        search = search.replace(' ', '%20')

        webbrowser.open(spotify_url + search)
    except Exception as e:
        print(f"webbrowser: {e}")


# frame for components
frame = Frame(root)

# ttk components
mainLabel = ttk.Label(frame, text = "Which one of these two Genres do you like the most?")
choose_a = tk.Button(frame, bg='#87ceeb', fg='#FFFFFF', command=optionAPropability)
choose_b = tk.Button(frame, bg='#87ceeb', fg='#FFFFFF', command=optionBPropability)
skip_button = tk.Button(frame, bg='#FF5252', text="Skip", fg='#FFFFFF', command=skip)
genreList = tk.Listbox(frame, width=40, height=20, border=0)
search = tk.Button(frame, text="Open in Spotify", bg="#1DB954", fg="#FFFFFF", command=searchFromSpotify)
quit = ttk.Button(root, text="QUIT", command=closeWindow)

writeJson(checked_list_json, readJson(genre_json))
update()


# Configure font-family, size, background color and height for labels.
mainLabel.config(font=("Helvetica", 16))
genreList.config(font=("Helvetica", 11), height=15, bg='#FFFFFF')
choose_a.config(font=("Helvetica", 13), height=3)
choose_b.config(font=("Helvetica", 13), height=3)
skip_button.config(font=("Helvetica", 13), height=1)

# grid
mainLabel.grid(row=0, column=1, padx=30, pady=40, sticky=N+S+E+W)
choose_a.grid(row=1, column=1, padx=25, pady=10, sticky=N+S+E+W)
choose_b.grid(row=2, column=1, padx=25, pady=10, sticky=N+S+E+W)
skip_button.grid(row=3, column=1,padx=25, pady=10, sticky=N+S+E+W)
genreList.grid(row=4, column=1, padx=25, pady=0, sticky=N+S+E+W)
search.grid(row=5, column=1, padx=25, pady=10, sticky=N+S+E+W)
quit.pack(side="bottom")
frame.pack() 

root.mainloop()
