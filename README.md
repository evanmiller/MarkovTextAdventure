Text Adventure Analysis
--

This is a Markov analysis of the [The Teeny Tiny Mansion](http://svn.clifford.at/handicraft/2017/tttm/README).

Usage:

    julia TextAdventure.jl

Typical output:

```
Scenario 2: Green-key bug only
 => There is a dead end :-(
   => Calculating how bad it is...
   => Still calculating...
 => This bug affects 25.00% of button-mashing players
# Valid states: 1664
MAX_FINISH_DEPTH: 14
Scenario 3: Help-me bug only
 => There is a dead end :-(
   => Calculating how bad it is...
   => Still calculating...
 => This bug affects 71.28% of button-mashing players
# Valid states: 1680
MAX_FINISH_DEPTH: 14
Scenario 4: No bugs (hopefully)
 => 59 recurrent classes and no dead ends! Hooray!
   => Verifying the result...
   => Still calculating...
 => This bug affects -0.00% of button-mashing players
# Valid states: 1664
MAX_FINISH_DEPTH: 14
```
