#coding: utf8
import requests
import bs4
import csv
import os
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool

# IMPORTANT NOTE: Each regional variant and other variants (such as Deoxys or Deerling forms) are also included

# Information that will be extracted for each Pokémon
# Possible values are:
# - DexNumber: Number of the Pokémon for the national dex
# - Name: Name of the Pokémon
# - Type: Pokémon's typing as a list
# - Abilities: Pokémon's abilities as a list
# - Generation: The generation where it was introduced
# - Hp: Hp base stat
# - Attack: Attack base stat
# - Defense: Defense base stat
# - SpecialAttack: Special attack base stat
# - SpecialDefense: Special defense base stat
# - Speed: Speed base stat
# - TotalStats: Total stats (sum of the previous six stats)
# - Weight: Weight in kg
# - Height: Height in m
# - GenderProbM: Probability of a Pokémon of that species being male (if it has unknown gender, it will be None)
# - Category: Category of that Pokémon (some distinct Pokémons have the same categories, and it may vary between evolutions)
# - CatchRate: Capture rate of that Pokémon
# - EggCycles: Number of cycles (steps, the number of steps in each cycle varies among games) to hatch an egg of that Pokémon
# - EggGroup: Egg Group(s) of that Pokémon
# - LevelingRate: Class of the XP growth of that Pokémon
# - BaseFriendship: Base friendship of that Pokémon
# - IsLegendary: Denotes if it is a legendary pokemon
# - IsLegendary: Denotes if it is a legendary pokemon
# - IsMythical: Denotes if it is a mythical pokemon
# - IsUltraBeast: Denotes if it is an ultra beast
# - HasMega: Has a Mega evolution
# - EvoStage: Evolution Stage of that Pokémon
# - TotalEvoStages: Total evolution stages for that Pokémon
# - PreevoName: Name of that Pokémon's preevolution
# - DamageFrom(Type): Amount of damage taken for a specific attack type

INFO = ['DexNumber', 'Name', 'Type', 'Abilities', 'Generation', 'Hp', 'Attack',
        'Defense', 'SpecialAttack', 'SpecialDefense', 'Speed',
        'TotalStats', 'Weight', 'Height', 'GenderProbM', 'Category',
        'CatchRate', 'EggCycles', 'EggGroup', 'LevelingRate',
        'BaseFriendship', 'IsLegendary', 'IsMythical', 'IsUltraBeast',
        'HasMega', 'EvoStage', 'TotalEvoStages', 'PreevoName', 'DamageFromNormal',
        'DamageFromFighting', 'DamageFromFlying', 'DamageFromPoison',
        'DamageFromGround', 'DamageFromRock', 'DamageFromBug', 'DamageFromGhost',
        'DamageFromSteel', 'DamageFromFire', 'DamageFromWater', 'DamageFromGrass',
        'DamageFromElectric', 'DamageFromPsychic', 'DamageFromIce', 'DamageFromDragon',
        'DamageFromDark', 'DamageFromFairy']

# Type chart. Attacking type in rows, defending type in columns
TYPECHART = pd.DataFrame([[1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 1.0, 0.0, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                          [2.0, 1.0, 0.5, 0.5, 1.0, 2.0, 0.5, 0.0, 2.0, 1.0, 1.0, 1.0, 1.0, 0.5, 2.0, 1.0, 2.0, 0.5],
                          [1.0, 2.0, 1.0, 1.0, 1.0, 0.5, 2.0, 1.0, 0.5, 1.0, 1.0, 2.0, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0],
                          [1.0, 1.0, 1.0, 0.5, 0.5, 0.5, 1.0, 0.5, 0.0, 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0],
                          [1.0, 1.0, 0.0, 2.0, 1.0, 2.0, 0.5, 1.0, 2.0, 2.0, 1.0, 0.5, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                          [1.0, 0.5, 2.0, 1.0, 0.5, 1.0, 2.0, 1.0, 0.5, 2.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 1.0],
                          [1.0, 0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 0.5, 0.5, 0.5, 1.0, 2.0, 1.0, 2.0, 1.0, 1.0, 2.0, 0.5],
                          [0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 0.5, 1.0],
                          [1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 0.5, 0.5, 0.5, 1.0, 0.5, 1.0, 2.0, 1.0, 1.0, 2.0],
                          [1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 2.0, 1.0, 2.0, 0.5, 0.5, 2.0, 1.0, 1.0, 2.0, 0.5, 1.0, 1.0],
                          [1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 1.0, 1.0, 1.0, 2.0, 0.5, 0.5, 1.0, 1.0, 1.0, 0.5, 1.0, 1.0],
                          [1.0, 1.0, 0.5, 0.5, 2.0, 2.0, 0.5, 1.0, 0.5, 0.5, 2.0, 0.5, 1.0, 1.0, 1.0, 0.5, 1.0, 1.0],
                          [1.0, 1.0, 2.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 0.5, 0.5, 1.0, 1.0, 0.5, 1.0, 1.0],
                          [1.0, 2.0, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 0.5, 1.0, 1.0, 1.0, 1.0, 0.5, 1.0, 1.0, 0.0, 1.0],
                          [1.0, 1.0, 2.0, 1.0, 2.0, 1.0, 1.0, 1.0, 0.5, 0.5, 0.5, 2.0, 1.0, 1.0, 0.5, 2.0, 1.0, 1.0],
                          [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 0.0],
                          [1.0, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 0.5, 0.5],
                          [1.0, 2.0, 1.0, 0.5, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 1.0]],
                          index = ['Normal', 'Fighting', 'Flying', 'Poison', 'Ground', 'Rock', 'Bug', 'Ghost', 'Steel',
                                  'Fire', 'Water', 'Grass', 'Electric', 'Psychic', 'Ice', 'Dragon', 'Dark', 'Fairy'],
                          columns = ['Normal', 'Fighting', 'Flying', 'Poison', 'Ground', 'Rock', 'Bug', 'Ghost', 'Steel',
                                  'Fire', 'Water', 'Grass', 'Electric', 'Psychic', 'Ice', 'Dragon', 'Dark', 'Fairy'])

MAIN_PAGE_URL = 'http://bulbapedia.bulbagarden.net'                                     # Main page's URL
NATIONAL_DEX_URL = MAIN_PAGE_URL + '/wiki/List_of_Pokémon_by_National_Pokédex_number'   # URL of the National Dex
CURRENT_FILE_PATH = os.path.dirname(os.path.abspath(__file__))                          # CSV path
REGIONAL_VARIATIONS = ['Alolan', 'Galarian', 'Hisuian', 'Paldean']

for elem in INFO:
    assert elem in ['DexNumber', 'Name', 'Type', 'Abilities', 'Generation', 'Hp', 'Attack',
        'Defense', 'SpecialAttack', 'SpecialDefense', 'Speed',
        'TotalStats', 'Weight', 'Height', 'GenderProbM', 'Category',
        'CatchRate', 'EggCycles', 'EggGroup', 'LevelingRate',
        'BaseFriendship', 'IsLegendary', 'IsMythical', 'IsUltraBeast',
        'HasMega', 'EvoStage', 'TotalEvoStages', 'PreevoName', 'DamageFromNormal',
        'DamageFromFighting', 'DamageFromFlying', 'DamageFromPoison',
        'DamageFromGround', 'DamageFromRock', 'DamageFromBug', 'DamageFromGhost',
        'DamageFromSteel', 'DamageFromFire', 'DamageFromWater', 'DamageFromGrass',
        'DamageFromElectric', 'DamageFromPsychic', 'DamageFromIce', 'DamageFromDragon',
        'DamageFromDark', 'DamageFromFairy']

all_pokemon_data = []   # This array will have all Pokémon data
scrapped_pokemon = []

def getPokémonName(link):
    text = ''
    if link.find_next_sibling('small') is None:
        text = link.text
    else:
        if link.find_next_sibling('small').text.split(" ")[0] in REGIONAL_VARIATIONS:
            text = f"{link.find_next_sibling('small').text.split()[0]} {link.text}"
        else:
            text = f"{link.text} {link.find_next_sibling('small').text}"
    
    # There can be some blanks at the end
    if text[-1] == " ":
        text = text[:-1]
    
    return text

def getPokemonUrls():
    """
    Get the URLs of all the Pokémon in the national dex of Pokémon 
    """
    listOfUrls = requests.get(NATIONAL_DEX_URL)                                 # Request to the national dex page, returning the result
    soup = bs4.BeautifulSoup( listOfUrls.text, "html.parser" )                  # Returns the document as a nested data structure
    
    """
    f = open(os.path.abspath(os.path.join(CURRENT_FILE_PATH, os.pardir)) + "/data/demofile3.txt", "w+")
    f.write(soup.prettify())
    f.close()
    """

    pkmn_links = soup.find_all('a', title=lambda t: t and "(Pokémon)" in t)     # Filter all the anchor that contains (Pokémon) in the title
        
    return {getPokémonName(link): link.get('href') for link in pkmn_links}                            # Only get the href parameter (URL)


def selectCorrectStats(name, form, stat_list):
    """
    Auxiliary function for selecting the stats from the corrent table in the URL
        Parameters:
            - form: Form of the Pokémon
            - stat_list: List containing all the a sections of those statistics
        Returns:
            - selected_index: Index containing the correct statistics location
    """
    # We need to calculate first the list of different possible forms that Pokémon has

    listforms = []
    for a in stat_list:
        if not a.parent.find_previous('h5') is None:
            listforms.append(a.parent.find_previous('h5').text)
        else:
            listforms.append('')

    if form == 'Galarian Darmanitan':                   # Exception
        form = 'Standard Mode'
    
    newform = form
    
    if not newform in listforms:
        newform = f"{name.split()[0]} {form}"
        if not newform in listforms:
            newform = f"{form} {name.split()[0]}"
            if not newform in listforms:
                if newform.split()[0] in REGIONAL_VARIATIONS:
                    newform = listforms[0]

    form = newform
    #print(form, listforms)
    #print("---")
    
    # After that, we will select the correct stats, according to its form, comparing the titles of the tables
    selected = False
    selected_index = len(listforms)-1
    while not selected and selected_index > -1:
        if form == listforms[selected_index]:
            if not(stat_list[selected_index].parent.find_next_sibling('div') is None) and not(len(stat_list[selected_index].parent.find_next_sibling('div').text) < 1) and not(len(stat_list[selected_index].parent.find_next_sibling('div').text) > 3):
                selected = True
        if not selected:
            selected_index -= 1

    # If the tables of the tables do not correspond to the form, we will select the last ones (most updated ones) containing valid values
    if not selected:
        selected_index = len(listforms)-1
        while not selected and selected_index > -1:
            if not(stat_list[selected_index].parent.find_next_sibling('div') is None) and not(len(stat_list[selected_index].parent.find_next_sibling('div').text) < 1) and not(len(stat_list[selected_index].parent.find_next_sibling('div').text) > 3):
                selected = True
            if not selected:
                selected_index -= 1

    print(stat_list[selected_index].parent.find_next_sibling('div').text)
    return selected_index


def getTypes(s, name, form):
    """
    Auxiliary function to return the Pokemon's types as a list (it wil lbe useful regarding type effectiveness)
        Parameters:
            - s: Beautiful soup object containing the webpage's code
            - name: Name of the Pokémon
            - form: Form of that Pokémon
        Returns:
            - types: List containing the types of the Pokémon 
    """
    types_occurrencies = s.find_all('a', href=lambda t: t and "(type)" in t)
    types = []
    j = 0
    while not types_occurrencies[j].find_next('small').get_text() in [None, '', name, form]:
        j = j+1
    types.append(types_occurrencies[j].get_text())
    if types_occurrencies[j+1].get_text() != 'Unknown':
        types.append(types_occurrencies[j+1].get_text())
    if types == ['Unknown']:
        types = [types_occurrencies[0].get_text()]
        if types_occurrencies[1].get_text() != 'Unknown':
            types.append(types_occurrencies[1].get_text())
    return types


def typeEffectiveness(types, attacktype):
    """
    Returns type efectiveness as a real number
        Parameters:
            - types: List of types of the Pokémon
            - attacktype: Type of the attack damaging the Pokémon
        Returns:
            - effectivenes: Real number indicating the effectiveness as a multiplicative factor
    """
    effectiveness = 1.0
    for t in types:
        effectiveness *= TYPECHART.loc[attacktype, t]
    return effectiveness


def auxEvoInfo():
    pass



def getPokemonData(name, inputUrl):   
    """
    Gets the data of a Pokémon given its URL, and appends to the array containing all information
        Parameters:
            - inputUrl: The Pokémon's URL
        Returns:
            - pokemonData: List containing the data for the given Pokémon, in the same order as in INFO
    """
    pokemonData = []                                                            # Initialization
    scrapped_pokemon.append(name)
    htmlData = requests.get(MAIN_PAGE_URL + inputUrl)                         # Request to that Pokémon's page, returning the result
    soup = bs4.BeautifulSoup(htmlData.text, "html.parser")                    # Returns the document as a nested data structure

    form = ''
    if name.split()[0] in REGIONAL_VARIATIONS:
        form = name
    else:
        if name == soup.select('h1#firstHeading')[0].get_text()[:-10]:
            form = name
        else:
            form = name[len(soup.select('h1#firstHeading')[0].get_text()[:-10])+1:]
    pokemontypes = None

    print("----")
    print(name)
    print(form)
    print("----")

    # Write the result from soup for testing
    f = open(os.path.abspath(os.path.join(CURRENT_FILE_PATH, os.pardir)) + "/data/demofile3.txt", "w+")
    f.write(soup.prettify())
    f.close()

    for elem in INFO:

        if elem == 'DexNumber':          # Get the National Pokedex ID of the Pokémon
            pokemonData.append((int) (soup.find_all('a', title=lambda t: t and "List of Pokémon by National Pokédex number" in t)[1].findChild().get_text()[1:]))
        
        elif elem == 'Name':             # Get the name of the Pokémon
            pokemonData.append(name)

        elif elem == 'Type':            # Get the types of the Pokémon as a list (if it has only 1, the list will only contain 1 element)
            types = getTypes(soup, name, form)
            pokemontypes = types
            pokemonData.append(types)
        
        elif elem == 'Abilities':       # Get the possible abilities of that Pokémon (including hidden abilities)
            abilities = soup.find('a', href=lambda t: t and "/wiki/Ability" in t).parent.find_next_sibling().find_all('a', title=lambda t: t and "(Ability)" in t)
            selected_abilities = []
            for elem in abilities:
                if elem.find_next('small').get_text() in ['', name, form, ' Hidden Ability', name + ' Hidden Ability', form + ' Hidden Ability']:
                    #print('A', elem.get_text(), elem.find_next('small').get_text())
                    selected_abilities.append(elem.get_text())
                #else:
                    #print(elem.get_text(), elem.find_next('small').get_text())
            selected_abilities = list(filter(('Cacophony').__ne__, selected_abilities))                # Remove noisy Cacophony abilities
            selected_abilities = list(filter(('').__ne__, selected_abilities))
            if len(selected_abilities) == 0:
                selected_abilities.append(abilities[0].get_text())
            #print(selected_abilities)
            pokemonData.append(selected_abilities)

        elif elem == 'Generation':
            generation = None
            regional = form.split()[0]
            if name == 'Basculin White-Striped Form':                   # only exception as in https://bulbapedia.bulbagarden.net/wiki/Regional_form
                generation = 'VIII'
            else:
                if regional in REGIONAL_VARIATIONS:
                    if regional == 'Alolan':
                        generation = 'VII'
                    elif regional in ['Galarian', 'Hisuian']:
                        generation = 'VIII'
                    elif regional == 'Paldean':
                        generation = 'IX'
                else:
                    generation = soup.find('a', string=lambda t: t and "Generation" in t).get_text().split()[1]
            #print(generation)
            pokemonData.append(generation)
        
        elif elem == 'Hp':              # Get the base HP stat of that Pokémon
            hp = soup.find_all('a', title=lambda t: t and "HP" in t)      # Filter all the anchor that contains (HP) in the title
            index = selectCorrectStats(name, form, hp)
            pokemonData.append((int) (hp[index].parent.find_next_sibling('div').text))

        elif elem == 'Attack':          # Get the base Attack stat of that Pokémon
            attack = soup.find_all('a', href=lambda t: t and "Stat#Attack" in t)      # Filter all the anchor that contains (Attack) in the title
            index = selectCorrectStats(name, form, attack)
            pokemonData.append((int) (attack[index].parent.find_next_sibling('div').text))

        elif elem == 'Defense':         # Get the base Defense stat of that Pokémon
            defense = soup.find_all('a', href=lambda t: t and "Stat#Defense" in t)      # Filter all the anchor that contains (Defense) in the title
            index = selectCorrectStats(name, form, defense)
            pokemonData.append((int) (defense[index].parent.find_next_sibling('div').text))

        elif elem == 'SpecialAttack':   # Get the base Special Attack stat of that Pokémon
            specialattack = soup.find_all('a', href=lambda t: t and "Stat#Special_Attack" in t)      # Filter all the anchor that contains (Special_Attack) in the title
            index = selectCorrectStats(name, form, specialattack)
            pokemonData.append((int) (specialattack[index].parent.find_next_sibling('div').text))

        elif elem == 'SpecialDefense':  # Get the base Special Defense stat of that Pokémon
            specialdefense = soup.find_all('a', href=lambda t: t and "Stat#Special_Defense" in t)      # Filter all the anchor that contains (Special_Defense) in the title
            index = selectCorrectStats(name, form, specialdefense)
            pokemonData.append((int) (specialdefense[index].parent.find_next_sibling('div').text))

        elif elem == 'Speed':           # Get the base Speed stat of that Pokémon
            speed = soup.find_all('a', href=lambda t: t and "Stat#Speed" in t)      # Filter all the anchor that contains (Speed) in the title
            index = selectCorrectStats(name, form, speed)
            pokemonData.append((int) (speed[index].parent.find_next_sibling('div').text))

        elif elem == 'TotalStats':      # Get the total stats (sum of the previous ones) of that Pokémon
            totalstats = soup.find_all('div', string=lambda t: t and "Total:" in t)[-1]      # Filter all the anchor that contains (Ability) in the title
            pokemonData.append((int) (totalstats.find_next_sibling().text))

        elif elem == 'Weight':          # Get the weight of the current Pokémon
            weight = soup.find('a', title=lambda t: t and "Weight" in t)
            pokemonData.append((float) (weight.parent.find_next_sibling().findChild().findChild().findChildren()[1].text[:-3]))

        elif elem == 'Height':          # Get the weight of the current Pokémon
            height = soup.find('a', text=lambda t: t and "Height" in t)
            pokemonData.append((float) (height.parent.find_next_sibling().findChild().findChild().findChildren()[1].text[:-3]))

        elif elem == 'GenderProbM':
            prob = 0.0
            maleProb = soup.find('span', string=lambda t: t and "% male" in t)
            femaleProb = soup.find('span', string=lambda t: t and "% female" in t)
            if maleProb is None:           # If we do not have information of the male gender
                if femaleProb is None:     # If we do not have information about the female gender => it has unknown gender
                    prob = '-'
                else:                       # If we do have information about the female ratio, it can only be female.
                    prob = 0.0
            else:                          # If not, we can directly take it.
                maleProb = (float) (maleProb.get_text()[:-6])
                prob = maleProb/100.0                        
            pokemonData.append(prob)
        
        elif elem == 'Category':
            category = soup.find('a', title=lambda t: t and "Pokémon category" in t)                    # We first extract the initial category
            possible_subclasses = category.findChildren('span', class_=lambda t: t and "explain" in t)  # But it can depend on its forms
            if len (possible_subclasses) > 0:                                                           # If that category depends on its forms
                altform = ' '.join(form.split(" ")[:-1]) + ' ' + name.split(" ")[0]     # Basculin case.
                found = False
                j = 0
                while not found and j < len(possible_subclasses):                       # We search for the correct category according to its name
                    elem = possible_subclasses[j]
                    #print(elem.get('title'), ', ', form, ', ', altform)
                    if elem.get('title') == form or elem.get('title') == altform:       # When found, we assign it
                        category = elem.get_text() + ' Pokémon'
                        found = True
                    j = j+1
                if not found:                                                           # If it was not found
                    category = possible_subclasses[0].get_text() + ' Pokémon'           # We assign the first category
            else:
                category = category.get_text()
            pokemonData.append(category)
        
        elif elem == 'CatchRate':
            rate = soup.find('a', title=lambda t: t and "Catch rate" in t).find_next('td').get_text().split()[0]
            pokemonData.append(rate)
        
        elif elem == 'EggCycles':
            cycles = soup.find('a', title=lambda t: t and "Egg cycle" in t).find_next('td').get_text().split()[0]
            pokemonData.append(cycles)

        elif elem == 'EggGroup':
            groups = []
            search = soup.find_all('a', title=lambda t: t and "(Egg Group)" in t)
            for e in search:
                if not e.get_text().split()[-1] in ["Group", "Groups"] and not e.get_text() == "No Eggs Discovered":
                    groups.append(e.get_text())
            if len(groups) == 0:
                groups = '-'
            else:
                groups = pd.unique(groups)
            pokemonData.append(groups)
        
        elif elem == 'LevelingRate':
            rate = soup.find('span', string=lambda t: t and "Leveling rate" in t).find_next('td').get_text()
            pokemonData.append(rate)

        elif elem == 'BaseFriendship':
            friendship = soup.find('span', string=lambda t: t and "Base friendship" in t).find_next('td').get_text()
            pokemonData.append(friendship)

        elif elem == 'IsLegendary':
            islegendary = 0
            if "Legendary Pokémon" in soup.find('script').get_text():
                islegendary = 1
            pokemonData.append(islegendary)
        
        elif elem == 'IsMythical':
            ismythical = 0
            if "Mythical Pokémon" in soup.find('script').get_text():
                ismythical = 1
            pokemonData.append(ismythical)
        
        elif elem == 'IsUltraBeast':
            isub = 0
            if "Ultra Beast" in soup.find('script').get_text():
                isub = 1
            pokemonData.append(isub)
        
        elif elem == 'HasMega':
            hasmega = 0
            if "Pokémon with Mega Evolutions" in soup.find('script').get_text():
                hasmega = 1
            pokemonData.append(hasmega)
        
        elif elem == 'EvoStage':
            # CUIDADO CON BASCULIN Y BASCULEGION
            # Coger el nombre como se cogía antes, con el primer title, para comparar

            ret = None
            posregional = form.split()[0]
            fullform = None
            realname = soup.find('title').get_text()[:-66]
            if posregional in REGIONAL_VARIATIONS:
                fullform = ' '.join(name.split()[1:]) + ' ' + posregional + ' Form'
            else:
                fullform = name
            found = False
            possible_stages = ["Unevolved", "First Evolution", "Second Evolution"]
            stage = None
            real_j = None
            k = 0
            # We first search if that Pokémon and form have a specific evolution chain
            while k < len(possible_stages) and not found:
                ts = soup.find_all('small', string=lambda t: t and possible_stages[k] in t)
                j = 0
                while not found and j < len(ts):
                    t = ts[j].find_parent('table').find_parent('table')
                    if not t is None:
                        x = t.find('small', string=lambda t: t and possible_stages[k] in t).find_next('span')
                        if not x is None:
                            x = x.get_text()
                            curform = t.find('small', string=lambda t: t and possible_stages[k] in t).find_next('span').find_next('small').get_text()
                            #print('x: ',x, ', curform: ', curform, ', fullform: ', fullform, ', realname: ', realname)
                            if x + ' ' + curform == fullform:
                                found = True
                                stage = possible_stages[k]
                                real_j = j
                    j = j+1
                k = k+1

            # In case there is, we choose it
            if found:
                if stage == "Unevolved":
                    ret = 1
                elif stage == "First Evolution":
                    ret = 2
                else:
                    ret = 3
            # If not, we choose the first evolution chain found
            else:
                if soup.find('small', string=lambda t: t and "Unevolved" in t) is None: # Phione's case, does not have an evolution chain at all
                    ret = 1
                else:
                    t = soup.find('small', string=lambda t: t and "Unevolved" in t).find_parent('table').find_parent('table')
                    if t is None:
                        t = soup.find('small', string=lambda t: t and "Unevolved" in t).find_parent('table')
                    unevolved = t.find('small', string=lambda t: t and "Unevolved" in t).find_next('span').get_text()
                    if unevolved == realname:
                        ret = 1
                    else:
                        if not t.find('small', string=lambda t: t and "First Evolution" in t) is None:
                            firstevo = t.find('small', string=lambda t: t and "First Evolution" in t).find_next('span').get_text()
                            if firstevo == realname:
                                ret = 2
                            else:
                                ret = 3
                        else:
                            ret = 1
            pokemonData.append(ret)

        elif elem == 'TotalEvoStages':
            ret = None
            posregional = form.split()[0]
            fullform = None
            realname = soup.find('title').get_text()[:-66]
            if posregional in REGIONAL_VARIATIONS:
                fullform = ' '.join(name.split()[1:]) + ' ' + posregional + ' Form'
            else:
                fullform = name
            found = False
            possible_stages = ["Unevolved", "First Evolution", "Second Evolution"]
            stage = None
            real_j = None
            k = 0
            # We first search if that Pokémon and form have a specific evolution chain, if it has, we choose it
            while k < len(possible_stages) and not found:
                ts = soup.find_all('small', string=lambda t: t and possible_stages[k] in t)
                j = 0
                while not found and j < len(ts):
                    t = ts[j].find_parent('table').find_parent('table')
                    if not t is None:
                        x = t.find('small', string=lambda t: t and possible_stages[k] in t).find_next('span')
                        if not x is None:
                            x = x.get_text()
                            curform = t.find('small', string=lambda t: t and possible_stages[k] in t).find_next('span').find_next('small').get_text()
                            #print('x: ',x, ', curform: ', curform, ', fullform: ', fullform, ', realname: ', realname)
                            if x + ' ' + curform == fullform:
                                found = True
                                stage = possible_stages[k]
                                real_j = j
                    j = j+1
                k = k+1

            # In case it was not found, we select the first one
            if not found:           # We select the first appearance
                real_j = 0

            #print("Found, with ", stage, 'and', real_j)
            if stage == "Second Evolution":                 # We already know it
                ret = 3
            else:
                if soup.find('small', string=lambda t: t and "Unevolved" in t) is None: # Phione's case, does not have an evolution chain at all
                    ret = 1
                else:
                    t = soup.find_all('small', string=lambda t: t and "Unevolved" in t)[real_j].find_parent('table').find_parent('table')   # We select the table
                    if t is None:
                        t = soup.find_all('small', string=lambda t: t and "Unevolved" in t)[real_j].find_parent('table')
                    if not t.find('small', string=lambda t: t and "Second Evolution" in t) is None:   # If it has a second evolution stage:
                        ret = 3
                    elif not t.find('small', string=lambda t: t and "First Evolution" in t) is None:  # If it has a first evolution stage:
                        ret = 2
                    else:                                                                                               # In any other case
                        ret = 1
            pokemonData.append(ret)

        elif elem == 'PreevoName':
            ret = None
            posregional = form.split()[0]
            fullform = None
            realname = soup.find('title').get_text()[:-66]
            if posregional in REGIONAL_VARIATIONS:
                fullform = ' '.join(name.split()[1:]) + ' ' + posregional + ' Form'
            else:
                fullform = name
            found = False
            possible_stages = ["Unevolved", "First Evolution", "Second Evolution"]
            stage = None
            real_j = None
            k = 0
            # We first search if that Pokémon and form have a specific evolution chain, if it has, we choose it
            while k < len(possible_stages) and not found:
                ts = soup.find_all('small', string=lambda t: t and possible_stages[k] in t)
                j = 0
                while not found and j < len(ts):
                    t = ts[j].find_parent('table').find_parent('table')
                    if not t is None:
                        x = t.find('small', string=lambda t: t and possible_stages[k] in t).find_next('span')
                        if not x is None:
                            x = x.get_text()
                            curform = t.find('small', string=lambda t: t and possible_stages[k] in t).find_next('span').find_next('small').get_text()
                            #print('x: ',x, ', curform: ', curform, ', fullform: ', fullform, ', realname: ', realname)
                            if x + ' ' + curform == fullform:
                                found = True
                                stage = possible_stages[k]
                                real_j = j
                    j = j+1
                k = k+1

            # In case it was not found, we select the first one
            # In case there is, we choose it
            if found:
                search_unevolved = soup.find_all('small', string=lambda t: t and "Unevolved" in t)[real_j]
            else:
                search_unevolved = soup.find('small', string=lambda t: t and "Unevolved" in t)
            
            if search_unevolved is None: # Phione's case, does not have an evolution chain at all
                ret = "No Preevolution"
            else:
                t = search_unevolved.find_parent('table').find_parent('table')
                if t is None:
                    t = search_unevolved.find_parent('table')
                unevolved = t.find('small', string=lambda t: t and "Unevolved" in t).find_next('span').get_text()
                if unevolved == realname:
                    ret = "No Preevolution"
                else:
                    if not t.find('small', string=lambda t: t and "First Evolution" in t) is None:
                        firstevo = t.find('small', string=lambda t: t and "First Evolution" in t).find_next('span')
                        #print(firstevo)
                        if firstevo.get_text() == realname:
                            realname = t.find('small', string=lambda t: t and "Unevolved" in t).find_next('span').get_text()
                            possible_variation = t.find('small', string=lambda t: t and "Unevolved" in t).find_next('span').find_next('small').get_text()
                        else:
                            realname = t.find('small', string=lambda t: t and "First Evolution" in t).find_next('span').get_text()
                            possible_variation = t.find('small', string=lambda t: t and "First Evolution" in t).find_next('span').find_next('small').get_text()

                        if possible_variation is None:
                            ret = realname
                        else:
                            if possible_variation.split()[0] in REGIONAL_VARIATIONS:
                                new_name = possible_variation.split()[0] + ' ' + realname
                            else:
                                new_name = realname + ' ' + possible_variation
                            
                            if new_name in scrapped_pokemon:
                                ret = new_name
                            else:
                                ret = realname
                    else:
                        ret = "No Preevolution"
            #print(ret)
            pokemonData.append(ret)


        elif elem == 'DamageFromNormal':
            if pokemontypes is None:                                            # If types have not been calculated yet
                pokemontypes = getTypes(soup, name, form)                       # We calculate them
            pokemonData.append(typeEffectiveness(pokemontypes, 'Normal'))       # Calculate and assign the effectiveness against the current type
        

        elif elem == 'DamageFromFighting':
            if pokemontypes is None:                                            # If types have not been calculated yet
                pokemontypes = getTypes(soup, name, form)                       # We calculate them
            pokemonData.append(typeEffectiveness(pokemontypes, 'Fighting'))       # Calculate and assign the effectiveness against the current type
        

        elif elem == 'DamageFromFlying':
            if pokemontypes is None:                                            # If types have not been calculated yet
                pokemontypes = getTypes(soup, name, form)                       # We calculate them
            pokemonData.append(typeEffectiveness(pokemontypes, 'Flying'))       # Calculate and assign the effectiveness against the current type
        

        elif elem == 'DamageFromPoison':
            if pokemontypes is None:                                            # If types have not been calculated yet
                pokemontypes = getTypes(soup, name, form)                       # We calculate them
            pokemonData.append(typeEffectiveness(pokemontypes, 'Poison'))       # Calculate and assign the effectiveness against the current type


        elif elem == 'DamageFromGround':
            if pokemontypes is None:                                            # If types have not been calculated yet
                pokemontypes = getTypes(soup, name, form)                       # We calculate them
            pokemonData.append(typeEffectiveness(pokemontypes, 'Ground'))       # Calculate and assign the effectiveness against the current type
        

        elif elem == 'DamageFromRock':
            if pokemontypes is None:                                            # If types have not been calculated yet
                pokemontypes = getTypes(soup, name, form)                       # We calculate them
            pokemonData.append(typeEffectiveness(pokemontypes, 'Rock'))       # Calculate and assign the effectiveness against the current type
        

        elif elem == 'DamageFromBug':
            if pokemontypes is None:                                            # If types have not been calculated yet
                pokemontypes = getTypes(soup, name, form)                       # We calculate them
            pokemonData.append(typeEffectiveness(pokemontypes, 'Bug'))       # Calculate and assign the effectiveness against the current type
        

        elif elem == 'DamageFromGhost':
            if pokemontypes is None:                                            # If types have not been calculated yet
                pokemontypes = getTypes(soup, name, form)                       # We calculate them
            pokemonData.append(typeEffectiveness(pokemontypes, 'Ghost'))       # Calculate and assign the effectiveness against the current type
        

        elif elem == 'DamageFromSteel':
            if pokemontypes is None:                                            # If types have not been calculated yet
                pokemontypes = getTypes(soup, name, form)                       # We calculate them
            pokemonData.append(typeEffectiveness(pokemontypes, 'Steel'))       # Calculate and assign the effectiveness against the current type
        

        elif elem == 'DamageFromFire':
            if pokemontypes is None:                                            # If types have not been calculated yet
                pokemontypes = getTypes(soup, name, form)                       # We calculate them
            pokemonData.append(typeEffectiveness(pokemontypes, 'Fire'))       # Calculate and assign the effectiveness against the current type
        

        elif elem == 'DamageFromWater':
            if pokemontypes is None:                                            # If types have not been calculated yet
                pokemontypes = getTypes(soup, name, form)                       # We calculate them
            pokemonData.append(typeEffectiveness(pokemontypes, 'Water'))       # Calculate and assign the effectiveness against the current type
        

        elif elem == 'DamageFromGrass':
            if pokemontypes is None:                                            # If types have not been calculated yet
                pokemontypes = getTypes(soup, name, form)                       # We calculate them
            pokemonData.append(typeEffectiveness(pokemontypes, 'Grass'))       # Calculate and assign the effectiveness against the current type
        

        elif elem == 'DamageFromElectric':
            if pokemontypes is None:                                            # If types have not been calculated yet
                pokemontypes = getTypes(soup, name, form)                       # We calculate them
            pokemonData.append(typeEffectiveness(pokemontypes, 'Electric'))       # Calculate and assign the effectiveness against the current type
        

        elif elem == 'DamageFromPsychic':
            if pokemontypes is None:                                            # If types have not been calculated yet
                pokemontypes = getTypes(soup, name, form)                       # We calculate them
            pokemonData.append(typeEffectiveness(pokemontypes, 'Psychic'))       # Calculate and assign the effectiveness against the current type
        

        elif elem == 'DamageFromIce':
            if pokemontypes is None:                                            # If types have not been calculated yet
                pokemontypes = getTypes(soup, name, form)                       # We calculate them
            pokemonData.append(typeEffectiveness(pokemontypes, 'Ice'))       # Calculate and assign the effectiveness against the current type
        

        elif elem == 'DamageFromDragon':
            if pokemontypes is None:                                            # If types have not been calculated yet
                pokemontypes = getTypes(soup, name, form)                       # We calculate them
            pokemonData.append(typeEffectiveness(pokemontypes, 'Dragon'))       # Calculate and assign the effectiveness against the current type
        

        elif elem == 'DamageFromDark':
            if pokemontypes is None:                                            # If types have not been calculated yet
                pokemontypes = getTypes(soup, name, form)                       # We calculate them
            pokemonData.append(typeEffectiveness(pokemontypes, 'Dark'))       # Calculate and assign the effectiveness against the current type
        

        elif elem == 'DamageFromFairy':
            if pokemontypes is None:                                            # If types have not been calculated yet
                pokemontypes = getTypes(soup, name, form)                       # We calculate them
            pokemonData.append(typeEffectiveness(pokemontypes, 'Fairy'))       # Calculate and assign the effectiveness against the current type

        
    return pokemonData


def allPokemonStats():
    """
    Get the stats of every Pokémon by going through every url and getting the info
    """
    pokemonUrls = getPokemonUrls()
    listkeys = list(pokemonUrls.keys()) 
    for i in tqdm(range(len(listkeys))):
        all_pokemon_data.append(getPokemonData(listkeys[i], pokemonUrls[listkeys[i]]))
        

def WriteListToCSV(csv_file,csv_columns,data_list):
    """
    Writes the list of information into a CSV file
        Parameters:
            - csv_file: Path of that CSV file
            - csv_columns: List containing the names for the CSV columns
            - data_list: List containing the information to save
    """
    with open(csv_file, 'w') as csvfile:
        writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(csv_columns)                    # Write the column names
        for data in data_list:
            writer.writerow(data)                       # Write the data   

# Testing
testing = False

if testing:

    getPokemonData('Galarian Darmanitan', '/wiki/Darmanitan_(Pokémon)')
    getPokemonData('Darmanitan Zen Mode(Galarian Form)', '/wiki/Darmanitan_(Pokémon)')
    getPokemonData('Necrozma', '/wiki/Necrozma_(Pokémon)')
    getPokemonData('Necrozma Dusk Mane', '/wiki/Necrozma_(Pokémon)')
    getPokemonData('Necrozma Dawn Wings', '/wiki/Necrozma_(Pokémon)')
    getPokemonData('Zacian Hero of Many Battles', '/wiki/Zacian_(Pokémon)')

    """
    getPokemonData('Basculin White-Striped Form', '/wiki/Basculin_(Pokémon)')
    getPokemonData('Galarian Linoone', '/wiki/Linoone_(Pokémon)')
    getPokemonData('Obstagoon', '/wiki/Obstagoon_(Pokémon)')
    getPokemonData('Basculegion', '/wiki/Basculegion_(Pokémon)')
    getPokemonData('Eevee', '/wiki/Eevee_(Pokémon)')
    getPokemonData('Phione', '/wiki/Phione_(Pokémon)')
    getPokemonData('Basculin Red-Striped Form', '/wiki/Basculin_(Pokémon)')
    getPokemonData('Basculin White-Striped Form', '/wiki/Basculin_(Pokémon)')
    getPokemonData('Nihilego', '/wiki/Nihilego_(Pokémon)')
    getPokemonData('Galarian Linoone', '/wiki/Linoone_(Pokémon)')
    getPokemonData('Nihilego', '/wiki/Nihilego_(Pokémon)')
    getPokemonData('Mew', '/wiki/Mew_(Pokémon)')
    getPokemonData('Vespiquen', '/wiki/Vespiquen_(Pokémon)')
    getPokemonData('Snorlax', '/wiki/Snorlax_(Pokémon)')
    getPokemonData('Ampharos', '/wiki/Ampharos_(Pokémon)')
    getPokemonData('Tyrogue', '/wiki/Tyrogue_(Pokémon)')
    getPokemonData('Exeggutor', '/wiki/Exeggutor_(Pokémon)')
    getPokemonData('Alolan Exeggutor', '/wiki/Exeggutor_(Pokémon)')
    getPokemonData('Dragonite', '/wiki/Dragonite_(Pokémon)')
    getPokemonData('Shiftry', '/wiki/Shiftry_(Pokémon)')
    getPokemonData('Deoxys Attack Forme', '/wiki/Deoxys_(Pokémon)')
    getPokemonData('Cresselia', '/wiki/Cresselia_(Pokémon)')
    getPokemonData('Alolan Sandshrew', '/wiki/Sandshrew_(Pokémon)')
    getPokemonData('Rattata', '/wiki/Rattata_(Pokémon)')
    getPokemonData('Charizard', '/wiki/Charizard_(Pokémon)')
    getPokemonData('Zacian Hero of Many Battles', '/wiki/Zacian_(Pokémon)')
    """
else:
    allPokemonStats()
    WriteListToCSV(os.path.abspath(os.path.join(CURRENT_FILE_PATH, os.pardir)) + "/data/Pokemon.csv", INFO, all_pokemon_data)