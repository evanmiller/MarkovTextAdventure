Markov Text Adventure Analysis
--

This is a Markov analysis of the [The Teeny Tiny Mansion](http://svn.clifford.at/handicraft/2017/tttm/README).
Please see [Evan Miller's blog](http://www.evanmiller.org/adventure-games-and-eigenvalues.html)
for the basic information on what this is supposed to do.

Usage:

    julia MarkovTextAdventure.jl

or

    python MarkovTextAdventure.py

Typical output:

```
Scenario 1: Green-key bug and help-me bug
 => There is a dead end :-(
   => Calculating how bad it is...
   => Still calculating...
 => This bug affects 78.46% of button-mashing players
 => Valid states: 1680
 => MAX_FINISH_DEPTH: 14
Scenario 2: Green-key bug only
 => There is a dead end :-(
   => Calculating how bad it is...
   => Still calculating...
 => This bug affects 25.00% of button-mashing players
 => Valid states: 1664
 => MAX_FINISH_DEPTH: 14
Scenario 3: Help-me bug only
 => There is a dead end :-(
   => Calculating how bad it is...
   => Still calculating...
 => This bug affects 71.28% of button-mashing players
 => Valid states: 1680
 => MAX_FINISH_DEPTH: 14
Scenario 4: No bugs (hopefully)
 => 59 recurrent classes and no dead ends! Hooray!
   => Verifying the result...
   => Still calculating...
 => This bug affects -0.00% of button-mashing players
 => Valid states: 1664
 => MAX_FINISH_DEPTH: 14
```

### Python differences

The Python port (contributed by [hackerb9](https://github.com/hackerb9)
has some differences from the Julia version.

Changes:
   * [MarkovTextAdventure.py](MarkovTextAdventure.py) runs on Python (2 and 3).
   * Uses Arnoldi Iteration and sparse arrays.
   * Runs faster, requires less memory.
   * Now works on CPUs from the 1990's which lack SSE2 (*woohoo!*).
   * Does not yet implement % button-masher code.
   
To do:
   * Calculate % of button-mashers affected.
   * Make matrix more sparse by culling actions that go "backward" .
   * Allow Alice and Bob to be eaten by a GRUE.

*NB: This is a work of ergodic fiction, suitable for appropriate age groups only.*
