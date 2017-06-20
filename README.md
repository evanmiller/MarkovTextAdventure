Markov Text Adventure Analysis
--

This is a port to Python of Evan Miller's Markov analysis of the [The
Teeny Tiny Mansion](http://svn.clifford.at/handicraft/2017/tttm/README).
Please see [Evan Miller's blog](http://evanmiller.org/adventure-game)
for the basic information on what this is supposed to do.

The main difference between [this code](MarkovTextAdventure.py) and
[Evan's](https://github.com/evanmiller/MarkovTextAdventure) is that
I've ported it to Python instead of Julia. However, it is also faster,
and lighter in memory.

Changes:
   * [MarkovTextAdventure.py](MarkovTextAdventure.py) now runs on Python (2 and 3)
   * Uses Arnoldi Iteration and sparse arrays to increase speed, reduce memory.
   * Now works on CPUs from the 1990's which lack SSE2 (*woohoo!*).

Yet to do:
   * Calculate % of button-mashers affected.
   * Make matrix more sparse by culling actions that go "backward" .

Usage:

    python MarkovTextAdventure.py

Typical output:

```
Scenario 1: Green-key bug and help-me bug
 => There is a dead end :-( 
   => Calculating how bad it is...
   => Still calculating...
 => This bug affects 98.44% of button-mashing players
    (Just kidding. We don't calculate that yet.)
 => Valid states: 1680
 => MAX_FINISH_DEPTH: 14

Scenario 2: Green-key bug only
 => There is a dead end :-( 
   => Calculating how bad it is...
   => Still calculating...
 => This bug affects 98.44% of button-mashing players
    (Just kidding. We don't calculate that yet.)
 => Valid states: 1664
 => MAX_FINISH_DEPTH: 14

Scenario 3: Help-me bug only
 => There is a dead end :-( 
   => Calculating how bad it is...
   => Still calculating...
 => This bug affects 97.92% of button-mashing players
    (Just kidding. We don't calculate that yet.)
 => Valid states: 1680
 => MAX_FINISH_DEPTH: 14

Scenario 4: No bugs (hopefully)
 => 59 recurrent classes and no dead ends! Hooray!
   => Verifying the result...
   => Still calculating...
 => This bug affects 97.92% of button-mashing players
    (Just kidding. We don't calculate that yet.)
 => Valid states: 1664
 => MAX_FINISH_DEPTH: 14
```

NB: This is a work of ergodic fiction, suitable for appropriate age groups only.

