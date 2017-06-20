#!/usr/bin/python

# This is hackerb9's port of Evan Miller's formal proof of
# "The Teeny-Tiny Mansion".
#
# Changes:
#   * Ported to Python from Julia.
#   * Uses Arnoldi Iteration and sparse arrays to increase speed, reduce memory.
#   * Now works on CPUs from the 1990's which lack SSE2 (woohoo!).
#   * Python2/3 agnostic.
#
# Yet to do:
#   * Calculate % of button-mashers affected.
#   * Make matrix more sparse by culling actions that go "backward" .
#
# NB: This is a work of ergodic fiction, for appropriate age groups only.

from time import time
import numpy as np
from scipy.sparse import eye, diags

from enum import Enum
class MyEnum(Enum):
    def index(self):
        return list(self.__class__).index(self)

CHAR=MyEnum('Character','ALICE BOB')
LOC=MyEnum('Location', 'WEST_ROOM EAST_ROOM RED_ROOM BLUE_ROOM')
OBJ=MyEnum('Object', 'RED_KEY BLUE_KEY GREEN_KEY')
OBJLOC=(LOC.WEST_ROOM, LOC.EAST_ROOM, CHAR.ALICE, CHAR.BOB)
OP=MyEnum('Operation', 'GOTO PICKUP GIVE SWITCH FINISH')
GAME_STATES = 2048

# Game play code ported from MarkovTextAdventure.jl
# http://www.evanmiller.org/adventure-games-and-eigenvalues.html

def query_actions(state):
    actions=[]

    current_location = None
    other_location = None

    if state['character'] == CHAR.ALICE:
        current_location = state['alice_location']
        other_location = state['bob_location']
    else:
        current_location = state['bob_location']
        other_location = state['alice_location']


    if state['alice_location'] == LOC.RED_ROOM and state['bob_location'] == LOC.BLUE_ROOM:
        actions.append({'op':OP.FINISH, 'arg1':None})

    actions.append({'op':OP.SWITCH, 'arg1':None})

    if state['red_key_location'] == current_location:
        actions.append({'op':OP.PICKUP, 'arg1':OBJ.RED_KEY})

    if state['blue_key_location'] == current_location:
        actions.append({'op':OP.PICKUP, 'arg1':OBJ.BLUE_KEY})

    if state['green_key_location'] == current_location:
        actions.append({'op':OP.PICKUP, 'arg1':OBJ.GREEN_KEY})

    if current_location == other_location:
        if state['red_key_location'] == state['character']:
            actions.append({'op':OP.GIVE, 'arg1':OBJ.RED_KEY})

        if state['blue_key_location'] == state['character']:
            actions.append({'op':OP.GIVE, 'arg1':OBJ.BLUE_KEY})

        if state['green_key_location'] == state['character']:
            actions.append({'op':OP.GIVE, 'arg1':OBJ.GREEN_KEY})

    if current_location == LOC.WEST_ROOM:
        actions.append({'op':OP.GOTO, 'arg1':LOC.RED_ROOM})
        actions.append({'op':OP.GOTO, 'arg1':LOC.EAST_ROOM})

    if current_location == LOC.EAST_ROOM:
        actions.append({'op':OP.GOTO, 'arg1':LOC.BLUE_ROOM})
        actions.append({'op':OP.GOTO, 'arg1':LOC.WEST_ROOM})

    if current_location == LOC.RED_ROOM:
        actions.append({'op':OP.GOTO, 'arg1':LOC.WEST_ROOM})

    if current_location == LOC.BLUE_ROOM:
        actions.append({'op':OP.GOTO, 'arg1':LOC.EAST_ROOM})

    return actions


def alice_needs_help(state):
    if state['red_key_location'] == CHAR.BOB:
        return True

    if state['green_key_location'] == CHAR.BOB:
        if state['red_key_location'] == LOC.EAST_ROOM:
            return True

        if state['alice_location'] == LOC.EAST_ROOM:
            return True

    if state['green_key_location'] == LOC.EAST_ROOM and state['alice_location'] != LOC.EAST_ROOM:
        return True

    return False

def bob_needs_help(state):
    if state['blue_key_location'] == CHAR.ALICE:
        return True

    if state['green_key_location'] == CHAR.ALICE:
        if state['blue_key_location'] == LOC.WEST_ROOM:
            return True

        if state['bob_location'] == LOC.WEST_ROOM:
            return True

    if state['green_key_location'] == LOC.WEST_ROOM and state['bob_location'] != LOC.WEST_ROOM:
        return True

    return False

def character_needs_help(state, action):
    if state['character'] == CHAR.ALICE and action['arg1'] == LOC.RED_ROOM:
        return bob_needs_help(state)

    if state['character'] == CHAR.BOB and action['arg1'] == LOC.BLUE_ROOM:
        return alice_needs_help(state)

    return False


def apply_action(state, action, bad_design):
    new_state = state.copy()

    current_location = None
    other_character_id = None

    if state['character'] == CHAR.ALICE:
        current_location = state['alice_location']
        other_character_id = CHAR.BOB
    else:
        current_location = state['bob_location']
        other_character_id = CHAR.ALICE

    if action['op'] == OP.GOTO:
        if state['red_key_location'] != state['character'] and action['arg1'] == LOC.RED_ROOM:
            return new_state

        if state['blue_key_location'] != state['character'] and action['arg1'] == LOC.BLUE_ROOM:
            return new_state

        if (state['green_key_location'] != state['character'] and
            ((current_location == LOC.WEST_ROOM and action['arg1'] == LOC.EAST_ROOM) or
             (current_location == LOC.EAST_ROOM and action['arg1'] == LOC.WEST_ROOM))):
            return new_state

        if state['character'] == CHAR.ALICE and current_location == LOC.RED_ROOM:
            return new_state

        if state['character'] == CHAR.BOB and current_location == LOC.BLUE_ROOM:
            return new_state

        if not bad_design:
            if character_needs_help(state, action):
                return new_state

        if state['character'] == CHAR.ALICE:
            new_state['alice_location'] = action['arg1']
        else:
            new_state['bob_location'] = action['arg1']

    if action['op'] == OP.PICKUP:
        if action['arg1'] == OBJ.RED_KEY:
            new_state['red_key_location'] = state['character']

        if action['arg1'] == OBJ.BLUE_KEY:
            new_state['blue_key_location'] = state['character']

        if action['arg1'] == OBJ.GREEN_KEY:
            new_state['green_key_location'] = state['character']

    if action['op'] == OP.GIVE:
        if action['arg1'] == OBJ.RED_KEY:
            new_state['red_key_location'] = other_character_id

        if action['arg1'] == OBJ.BLUE_KEY:
            new_state['blue_key_location'] = other_character_id

        if action['arg1'] == OBJ.GREEN_KEY:
            new_state['green_key_location'] = other_character_id

    if action['op'] == OP.SWITCH:
        if state['character'] == CHAR.ALICE:
            new_state['character'] = CHAR.BOB
        else:
            new_state['character'] = CHAR.ALICE

    return new_state


def valid_initial_state(state, bad_design):
    if state['alice_location'] != LOC.WEST_ROOM and state['alice_location'] != LOC.EAST_ROOM:
        return False

    if state['bob_location'] != LOC.WEST_ROOM and state['bob_location'] != LOC.EAST_ROOM:
        return False

    if state['red_key_location'] != LOC.WEST_ROOM and state['red_key_location'] != LOC.EAST_ROOM:
        return False

    if state['blue_key_location'] != LOC.WEST_ROOM and state['blue_key_location'] != LOC.EAST_ROOM:
        return False

    if state['green_key_location'] != LOC.WEST_ROOM and state['green_key_location'] != LOC.EAST_ROOM:
        return False

    if not bad_design:
        if (state['alice_location'] == state['bob_location'] and
            state['alice_location'] != state['green_key_location']):
            return False

    return True

# Index-mapping code

# Bits		Meaning
# 0		Which character is active
# 1, 2		Which room Alice is in
# 3, 4		Which room Bob is in
# 5, 6		Which room or character the red key is in
# 7, 8		Which room or character the blue key is in
# 9, 10		Which room or character the green key is in
#
# Note that "location" of objects can be either W/E room or a character!

def index_for_state(state):
    """Encode the state as an 11-bit number"""
    
    index_zero = 0

    index_zero |= OBJLOC.index(state['green_key_location'])

    index_zero <<= 2
    index_zero |= OBJLOC.index(state['blue_key_location'])

    index_zero <<= 2
    index_zero |= OBJLOC.index(state['red_key_location'])

    index_zero <<= 2
    index_zero |= state['bob_location'].index()

    index_zero <<= 2
    index_zero |= state['alice_location'].index()

    index_zero <<= 1
    index_zero |= state['character'].index()

    return index_zero

def state_for_index(index):
    state={"character":None,
           "alice_location":None,
           "bob_location":None,
           "red_key_location":None,
           "blue_key_location":None,
           "green_key_location":None}

    if index >= GAME_STATES:
        return state

    index_zero = index

    state['character'] = CHAR((index_zero & 0x01) + 1)
    index_zero >>= 1

    state['alice_location'] = LOC((index_zero & 0x03) + 1)
    index_zero >>= 2

    state['bob_location'] = LOC((index_zero & 0x03) + 1)
    index_zero >>= 2

    state['red_key_location'] = OBJLOC[(index_zero & 0x03)]
    index_zero >>= 2

    state['blue_key_location'] = OBJLOC[(index_zero & 0x03)]
    index_zero >>= 2

    state['green_key_location'] = OBJLOC[(index_zero & 0x03)]
    index_zero >>= 2

    assert index_zero == 0

    return state


def valid_initial_index(i, bad_design):
    return valid_initial_state(state_for_index(i), bad_design)

# Analysis code

def fill_transition_matrix(matrix, bad_design, indexes):
    # Normal transitions
    for i in range(GAME_STATES):
        state = state_for_index(i)
        actions = query_actions(state)
        for j in actions:
            if j['op'] == OP.FINISH:
                matrix[i,-1] += 1.0/len(actions)
            else:
                new_state = apply_action(state, j, bad_design)
                matrix[i,index_for_state(new_state)] += 1.0/len(actions)

    # Game over: restart from valid start states
    for i in indexes:
        matrix[-1,i] = 1.0/len(indexes)

from scipy.sparse.linalg import eigs
def count_unit_eigenvalues(transition_matrix, k=2):
    print("   => Searching sparse matrix for eigenvectors...")
    t=time()
    count=k
    while k==count:
        k=2*k
        levalues, levectors = eigs(transition_matrix.H, sigma=0.999999999, k=k)
        count = np.count_nonzero( abs(levalues-1.0) < 1e-9 )
    print("      %g seconds" % (time()-t))
    return count

for i in range(GAME_STATES):
    assert i == index_for_state(state_for_index(i)) 

def analyze_game(bad_setup, bad_move):
    # Use LIL (LInked List) for building the matrix
    from scipy.sparse import lil_matrix

    transition_matrix1 = lil_matrix( (GAME_STATES+1,GAME_STATES+1) ) # P
    transition_matrix2 = lil_matrix( (GAME_STATES+1,GAME_STATES+1) ) # P*

    initial_states = []
    for i in range(GAME_STATES):
        if valid_initial_index(i, bad_setup):
            initial_states.append(i)

    fill_transition_matrix(transition_matrix1, bad_move, [-1])
    fill_transition_matrix(transition_matrix2, bad_move, initial_states)

    # Convert to compressed sparse row format for faster manipulation
    transition_matrix1=transition_matrix1.tocsr()
    transition_matrix2=transition_matrix2.tocsr()

    ev1 = count_unit_eigenvalues(transition_matrix1)
    ev2 = count_unit_eigenvalues(transition_matrix2)

    if ev1 == ev2:
        print(" => %d recurrent classes and no dead ends! Hooray!" % (ev1))
        print("   => Verifying the result...")
    else:
        print(" => There is a dead end :-( ")
        print("   => Calculating how bad it is...")

    state_vector = np.zeros(GAME_STATES+1)
    for i in initial_states:
        state_vector[i] = 1.0/len(initial_states)

    # Use the eigendecomposition to compute lim t->infty U*L^t*U^-1
    # Eigenvalues less than one will go to zero in the diagonal matrix.
    revalues, revectors = eigs(transition_matrix1)
    revectors=revectors.T
    
    diagonal_vector = np.zeros(GAME_STATES+1)
    for i,value in enumerate(revalues):
        if abs(value - 1.0) < 1e-9:
            diagonal_vector[i] = 1.0

    # XXX THIS HAS NOT BEEN IMPLEMENTED YET
    print("   => Still calculating...") # The "division" is basically a matrix inversion
    p = revectors * diags(diagonal_vector) / revectors
    final_state = (p * state_vector).real 
    print(" => This bug affects %.2f%% of button-mashing players" %
          ((1.0-final_state[-1])*100)[0])
    print("    (Just kidding. We don't calculate that yet.)")

    valid_states = []
    # Approximation for p, which seems to have a lot of floating-point jitter
    t = eye(GAME_STATES+1)
    for i in range(20):
        # Run the transition matrix until the # of non-zeros stops changing
        nnz=t.nnz
        t=t*transition_matrix1
        if nnz==t.nnz: break

    for i, j in enumerate(t[:-1,-1]):
        if j.real > 1e-8:
            valid_states.append(i)

    print(" => Valid states: %d" % (len(valid_states)))

    t = eye(GAME_STATES+1)
    for i in range(1, 21):
        t *= transition_matrix1
        can_be_finished = True
        for j in valid_states:
            if t[j,-1] == 0:
                can_be_finished = False
                break
        if can_be_finished:
            print(" => MAX_FINISH_DEPTH: %d\n" % (i))
            break


print("Scenario 1: Green-key bug and help-me bug")
analyze_game(True, True)

print("Scenario 2: Green-key bug only")
analyze_game(True, False)

print("Scenario 3: Help-me bug only")
analyze_game(False, True)

print("Scenario 4: No bugs (hopefully)")
analyze_game(False, False)

