### Welcome to Neural Gin Rummy:
For almost two decades, I've had a dream of dabbling with genetic algorithms and just never seemed to have the time to make it happen. One day I realized, life's too short to not dabble with genetic algorithms, and so this project was born. This is my first decent-sized foray into the python landscape and so far I'm loving it. I hope you have some fun as well!

The simulation is a python-based player-free Gin Rummy game. The strategy is evolved via neuralevolution. Test code and a sample playground.py is provided, along with a ~40000 generation persistence file.

Use it and abuse it!

***

To run this code, you'll need to install the following modules:

* pylru
* texttable

***

To get started, open a console and run:

` python playground.py`

This will launch the algorithm. You may want to observe the output -- this can be done in a second console window like so:

` tail -f playground_check_intelligence.persist.txt`

You can kill the script with Ctrl-C, which will trigger persistence handling and save the current generation to disk to be loaded again at next startup. As coded, it will then run a couple of games with the two best strategies and display the turn-by-turn output.

***


Additional per-generation fitness history is logged to the file:
* playground_check_intelligence.persist.txt.tally

Format is: generation,%skill win rate,score

You can download and use http://www.live-graph.org/ to watch the fitness output in real-time.

### Brief Overview

The majority of work is done in the GinMatch class, called as part of the fitness test. This class pits two players against each other in a "match" of gin rummy. Technically, a match is a number of games played until one player has 100 points, at which point the match is over and final scoring occurs. In this simulation (as of this writing), the population has not evolved sufficiently to play a full match. Presently, a match consists of a single game.

## Ranking Function and Output

The (as of this writing) ranking function looks at the percentage of games won WITHOUT a coinflip. In the case that a deck runs out or the players take too many moves, we use a coinflip to end the game. Games ending in coinflips are not useful for our long-term goal of developing a strong AI, so we don't include them in the ranking function.

The output for each generation looks something like this:

                     LEADERBOARD FOR GENERATION #47182  (population: 16
    +-----------------------------------------------------------------------------------------------------------+
    |  ranking      skill       score       skill     coinflip      game        match       match        age    |
    |             game win                game wins   game wins    losses       wins       losses               |
    |             rate (%)                                                                                      |
    +===========================================================================================================+
    | 1           0.357       0.333       5           1           9           6           9           0         |
    | 2           0.556       0.333       5           6           4           11          4           0         |
    | 3           0.385       0.333       5           2           8           7           8           0         |
    | ...                                                                                                       |
    +-----------------------------------------------------------------------------------------------------------+

Columns are explained as:
* ranking
* skill game win rate (%): this is how often a strategy wins WITHOUT a coinflip
* score: basically skill game win rate averaged by age
* skill game wins: number of games won without a coinflip
* game losses
* match wins: currently matches are 1 game long, so this is mostly filler for later
* match losses: same
* age


### Unimplemented Features:
* When a player knocks falsely, his hand should be exposed to the other player. -- not implemented
* The cull() function kills all individuals except the ones we're mating for the next generation. It should instead retain the top N individuals. -- not implemented
* Multithreading (4-8x speedup potential) -- not implemented
* Smarter initial weights (100-1000x speedup potential) -- not implemented
* Let the InputPerceptrons pull data from Observables, rather than Observables pushing data to Observers on each change (5% speedup potential) -- not implemented
* Faster key generation for memoized() (5-10% speedup) -- not implemented


### Authors and Contributors
All content licensed under [Creative Commons Attribution-ShareAlike 4.0 International](http://creativecommons.org/licenses/by-sa/4.0/). Improve and Share!

### Support or Contact
Drop me a note at [/u/rickthegrower](http://www.reddit.com/user/rickthegrower/)
