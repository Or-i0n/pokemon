"""After pressing RUN, enter a pokemon's name and don't worry about spelling mistakes or leave the userinput empty."""

import csv
from http import client 
import random
from typing import IO, Iterator, Union, List, Dict
from urllib import request, error


class Pokemon:
    """Defines a Pokemon."""

    def __init__(self) -> None:
        """Initializes Pokemon with datapath, data headers, pokemon names
        and all other info about pokemons."""

        # Web link of the dataset, hosted on github.
        self.datapath: str = ("https://raw.githubusercontent.com/Or-i0n/"
                              "pokemon/master/dataset.csv")
        # CSV headers of dataset.
        self.headers: List[str]
        # List of all pokemon names.
        self.names: List[str] = []
        # Dataset converted to dictionary form CSV file.
        # Holds all info about 800 pokemons.
        self.stats: Dict[int, List[str]] = self.fetch()
        


    def fetch(self) -> Dict[int, List[str]]:
        """Fetches a csv file and then convert it and return it as a dict."""

        # Holds all pokemon stats before this function sends it to self.stats.
        stats: Dict[int, List[str]] = {}

        # Fetch dataset from github
        try:
            # Requests github for csv dataset.
            raw : client.HTTPResponse = request.urlopen(self.datapath)
            # Converts dataset into string then to a list of lines.
            response: List[str] = raw.read().decode().splitlines()
        except error.URLError:
            print("Dataset Error! Failed to fetch dataset.")
            quit()
        else:
            # Reads CSV string lines.
            csv_reader: Iterator = csv.reader(response)

            # Iteratre over each line in CSV file.
            for rownum, row in enumerate(csv_reader):
                # Get all headers as a list
                if rownum == 0:
                    self.headers = row
                else:
                    # Push data to a dictionary
                    pokeid: int = rownum
                    # Other stats includes id, name, type and so on.
                    other_stats: List[str] = row
                    stats[pokeid] = other_stats
                    # Append names to a separate list.
                    self.names.append(row[1])

        return stats 


    def get(self, find: str) -> Union[Dict[str, str], None]:
        """Return the stats of a pokemon as a dict if a match is found
           else returns None.
           Note: Matching process is case-insensitive."""

        # Holds data of a single pokemon.
        info: Dict[str, str] = {}

        # Loop over each stat.
        for each in self.stats.values():
            name: str = each[1].lower()
            # Match is case-insensitive.
            if name == find.lower():
                # Push stats with there respective headers to info dict.
                for key, val in zip(self.headers, each):
                    info[key] = val

                return info


    def randname(self) -> str:
        """Returns a random name of a pokemon."""

        # Generates a random row number.
        randnum = random.randrange(800)
        name: str = ""

        # Loop over each row.
        for num, each in enumerate(self.stats.values()):
            # If iterator is on the same row as randnum return the name from 
            # the stat.
            if num == randnum:
                name = each[1]
                break

        return name


class Suggest:
    def lev_distance(self, str1: str, str2: str) -> int:
        """Returns Levenshtein distance (LD) which is a measure
        of the similarity between two strings. The distance is the number of
        deletions, insertions, or substitutions required to transform str1
        into str2."""

        # To equalize both strings lowercase them.
        str1, str2 = str1.lower(), str2.lower()

        # Create a matrix to compare two strings.
        matrix: List[List[int]] = []

        # First row of the matrix.
        matrix.append([index for index in range(len(str1) + 1)])

        # Fill first row and column with string index and rest with zeros.
        for row in range(len(str2)):
            matrix.append([row + 1])
            # _col is not used anywhere, just used for readablity.
            for _col in range(len(str1)):
                matrix[row + 1].append(0)

        # Calculate edit distance.
        for index2 in range(len(str2)):
            for index1 in range(len(str1)):
                # Calculate distance cost when both the character are similar.
                if str2[index2] == str1[index1]:
                    matrix[index2 + 1][index1 + 1] = matrix[index2][index1]
                # Calculate distance cost when both the characters are
                # different.
                else:
                    top = matrix[index2][index1]
                    left = matrix[index2][index1 + 1]
                    bottom = matrix[index2 + 1][index1]

                    min_of_three = min([top, left, bottom])

                    matrix[index2 + 1][index1 + 1] = min_of_three + 1

        # Return the distance calculated after all the process.
        return matrix[-1][-1]

    def suggestions(self, database: List[str], user_input: str) -> List[str]:
        """Handles suggestion process and returns spelling corrections.        
        Note: Suggestion process is case-insensitive."""

        direct_suggestions: List[str] = []
        hit_dict: Dict[str, int] = {}

        # Compare user input with words in database.
        for word in database:
            # If there is a direct match for that string in any of the
            # database's word then add that to a list.
            if user_input in word.lower():
                direct_suggestions.append(word)
            # Calculate and store edit distance of user input with each word
            # in database
            hit_dict[word] = self.lev_distance(user_input, word)

        # If there are any direct suggestions return them
        if direct_suggestions:
            return direct_suggestions

        # Else search for best match according to edit distance and add that to
        # the list
        best_match: List[str] = []
        for word in hit_dict:
            if hit_dict[word] == min(hit_dict.values()):
                best_match.append(word)

        return best_match


class App:
    """Defines the app."""

    def __init__(self):
        """Initializes app with objects form classes like Suggest, Pokemon.
           Also holds a random pokemon names then asks for a userinput and
           then show the stats of a pokemon."""

        self.suggest: Suggest = Suggest()
        self.pokemon: Pokemon = Pokemon()
        self.randname: str = self.pokemon.randname()
        # If the user doesn't provide an input it selects a random pokemon 
        # name.
        self.user: str = input()
        self.userinput: str = self.user or self.randname
        self.showinfo(self.userinput)

    
    def showinfo(self, userinput: str) -> None:
        """Shows pokemon stats in a beautiful way."""

        info: Union[Dict[str, str], None] = self.pokemon.get(userinput)
        
        # If finds a pokemon with the spelling provided.
        if info:
            if not self.user:
                print(f"Picking a random name '{self.userinput}'\n")
            else:
                print(f"Showing info about '{self.user}'\n")
           
            for key, val in info.items():
                print(f"{' ':8s}{key:10s} {val}")
        else:
            # Suggest pokemon names based on userinput.
            suggestions: List[str] = self.suggest.suggestions(
                                                         self.pokemon.names,
                                                         self.userinput)
            suggestions_len = len(suggestions)

            if suggestions_len == 1:
                print(f"Showing results for '{suggestions[0]}' instead of\n"
                      f"'{self.userinput}'\n")
                self.showinfo(suggestions[0])
            elif suggestions_len <= 5:
                print(f"Pokemon Not Found! Can't find '{self.userinput}'.\n\n"
                      "Did you mean?")
                for suggestion in suggestions:
                    print(f"● {suggestion}")
            else:
                print(f"There are {suggestions_len} matches found for your\n"
                      "query, please be more specific!\n")


app = App()
