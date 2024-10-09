# PokemonDataScience
This is a Data Science project, whose 3 main objectives are:
1. Generation of a dataset containing information about all Pokémons (until generation IX) including all variants and forms.
2. Preprocessing of that dataset, extraction of basic information and visualizations.
3. Apply Data Science Techniques in order to calculate higher level information and visualizations.


## Part 1: Dataset creation: Web scraping from Bulbapedia
To generate the Pokémon dataset, a web scraper has been programmed using Python, to get all the information required from [Bulbapedia](https://bulbapedia.bulbagarden.net/wiki/Main_Page). The information is stored in a csv file, in which, for each Pokémon and form in rows, the following information is extracted:
- **DexNumber**: Number of the National Pokédex for that Pokémon.
- **Name**: Name of the Pokémon.
- **Type**: Pokémon's typing as a list.
- **Abilities**: Pokémon's abilities as a list.
- **Generation**: The generation where it was introduced.
- **Hp**: Hp base stat.
- **Attack**: Attack base stat.
- **Defense**: Defense base stat.
- **SpecialAttack**: Special attack base stat.
- **SpecialDefense**: Special defense base stat.
- **Speed**: Speed base stat.
- **TotalStats**: Total stats (sum of the previous six stats).
- **Weight**: Weight in kg.
- **Height**: Height in m.
- **GenderProbM**: Probability of a Pokémon of that species being male (if it has unknown gender, it will be None).
- **Category**: Category of that Pokémon (some distinct Pokémons have the same categories, and it may vary between evolutions).
- **CatchRate**: Capture rate of that Pokémon.
- **EggCycles**: Number of cycles (steps, the number of steps in each cycle varies among games) to hatch an egg of that Pokémon.
- **EggGroup**: Egg Group(s) of that Pokémon.
- **LevelingRate**: Class of the XP growth of that Pokémon.
- **BaseFriendship**: Base friendship of that Pokémon.
- **IsLegendary**: Denotes if it is a legendary Pokémon.
- **IsLegendary**: Denotes if it is a legendary Pokémon.
- **IsMythical**: Denotes if it is a mythical Pokémon.
- **IsUltraBeast**: Denotes if it is an ultra beast.
- **HasMega**: Has a Mega evolution.
- **EvoStage**: Evolution Stage of that Pokémon.
- **TotalEvoStages**: Total evolution stages for that Pokémon.
- **DamageFrom(Type)**: Amount of damage taken for a specific attack type.

Information about Pokémon moves is currently not extracted.

## Part 2: Dataset cleaning and analysis: Python preprocessing and visualizations
In progress...

## Part 3: Data Science: Supervised and Unsupervised Learning, higher level information
In progress...

## Credits
David Villar Martos
