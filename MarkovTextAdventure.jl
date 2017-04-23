
type GameState
    character::Int;
	alice_location::Int
	bob_location::Int
	red_key_location::Int
	blue_key_location::Int
	green_key_location::Int
end

type GameAction
    op::Int
    arg1::Int
end

const CHAR_ALICE = 1
const CHAR_BOB = 2

const LOC_WEST_ROOM = 3
const LOC_EAST_ROOM = 4
const LOC_RED_ROOM = 5
const LOC_BLUE_ROOM = 6

const OBJ_RED_KEY = 7
const OBJ_BLUE_KEY = 8
const OBJ_GREEN_KEY = 9

const OP_GOTO = 10
const OP_PICKUP = 11
const OP_GIVE = 12
const OP_SWITCH = 13
const OP_FINISH = 14

const GAME_STATES = 2048

# Game play code ported from tttm.c
# http://svn.clifford.at/handicraft/2017/tttm/tttm.c

function query_actions(state::GameState)
    actions = Array{GameAction}(0)

    current_location = 0
    other_location = 0

    if state.character == CHAR_ALICE
        current_location = state.alice_location
        other_location = state.bob_location
    else
        current_location = state.bob_location
        other_location = state.alice_location
    end

    if state.alice_location == LOC_RED_ROOM && state.bob_location == LOC_BLUE_ROOM
        push!(actions, GameAction(OP_FINISH, 0))
    end

    push!(actions, GameAction(OP_SWITCH, 0))

    if state.red_key_location == current_location
        push!(actions, GameAction(OP_PICKUP, OBJ_RED_KEY))
    end

    if state.blue_key_location == current_location
        push!(actions, GameAction(OP_PICKUP, OBJ_BLUE_KEY))
    end

    if state.green_key_location == current_location
        push!(actions, GameAction(OP_PICKUP, OBJ_GREEN_KEY))
    end

    if current_location == other_location
        if state.red_key_location == state.character
            push!(actions, GameAction(OP_GIVE, OBJ_RED_KEY))
        end

        if state.blue_key_location == state.character
            push!(actions, GameAction(OP_GIVE, OBJ_BLUE_KEY))
        end

        if state.green_key_location == state.character
            push!(actions, GameAction(OP_GIVE, OBJ_GREEN_KEY))
        end
    end

    if current_location == LOC_WEST_ROOM
        push!(actions, GameAction(OP_GOTO, LOC_RED_ROOM))
        push!(actions, GameAction(OP_GOTO, LOC_EAST_ROOM))
    end

    if current_location == LOC_EAST_ROOM
        push!(actions, GameAction(OP_GOTO, LOC_BLUE_ROOM))
        push!(actions, GameAction(OP_GOTO, LOC_WEST_ROOM))
    end

    if current_location == LOC_RED_ROOM
        push!(actions, GameAction(OP_GOTO, LOC_WEST_ROOM))
    end

    if current_location == LOC_BLUE_ROOM
        push!(actions, GameAction(OP_GOTO, LOC_EAST_ROOM))
    end

    return actions
end

function alice_needs_help(state::GameState)
    if state.red_key_location == CHAR_BOB
        return true
    end

    if state.green_key_location == CHAR_BOB
        if state.red_key_location == LOC_EAST_ROOM
            return true
        end

        if state.alice_location == LOC_EAST_ROOM
            return true
        end
    end

    if state.green_key_location == LOC_EAST_ROOM && state.alice_location != LOC_EAST_ROOM
        return true
    end

    return false
end

function bob_needs_help(state::GameState)
    if state.blue_key_location == CHAR_ALICE
        return true
    end

    if state.green_key_location == CHAR_ALICE
        if state.blue_key_location == LOC_WEST_ROOM
            return true
        end

        if state.bob_location == LOC_WEST_ROOM
            return true
        end
    end

    if state.green_key_location == LOC_WEST_ROOM && state.bob_location != LOC_WEST_ROOM
        return true
    end

    return false
end

function character_needs_help(state::GameState, action::GameAction)
    if state.character == CHAR_ALICE && action.arg1 == LOC_RED_ROOM
        return bob_needs_help(state)
    end

    if state.character == CHAR_BOB && action.arg1 == LOC_BLUE_ROOM
        return alice_needs_help(state)
    end

    return false
end

function apply_action(state::GameState, action::GameAction, bad_design::Bool)
    new_state = deepcopy(state)

    current_location = 0
    other_character_id = 0

    if state.character == CHAR_ALICE
        current_location = state.alice_location
        other_character_id = CHAR_BOB
    else
        current_location = state.bob_location
        other_character_id = CHAR_ALICE
    end

    if action.op == OP_GOTO
        if state.red_key_location != state.character && action.arg1 == LOC_RED_ROOM
            return new_state
        end

        if state.blue_key_location != state.character && action.arg1 == LOC_BLUE_ROOM
            return new_state
        end

        if state.green_key_location != state.character &&
            ((current_location == LOC_WEST_ROOM && action.arg1 == LOC_EAST_ROOM) ||
            (current_location == LOC_EAST_ROOM && action.arg1 == LOC_WEST_ROOM))
            return new_state
        end

        if state.character == CHAR_ALICE && current_location == LOC_RED_ROOM
            return new_state
        end

        if state.character == CHAR_BOB && current_location == LOC_BLUE_ROOM
            return new_state
        end

        if !bad_design
            if character_needs_help(state, action)
                return new_state
            end
        end

        if state.character == CHAR_ALICE
            new_state.alice_location = action.arg1
        else
            new_state.bob_location = action.arg1
        end
    end

    if action.op == OP_PICKUP
        if action.arg1 == OBJ_RED_KEY
            new_state.red_key_location = state.character
        end

        if action.arg1 == OBJ_BLUE_KEY
            new_state.blue_key_location = state.character
        end

        if action.arg1 == OBJ_GREEN_KEY
            new_state.green_key_location = state.character
        end
    end

    if action.op == OP_GIVE
        if action.arg1 == OBJ_RED_KEY
            new_state.red_key_location = other_character_id
        end

        if action.arg1 == OBJ_BLUE_KEY
            new_state.blue_key_location = other_character_id
        end

        if action.arg1 == OBJ_GREEN_KEY
            new_state.green_key_location = other_character_id
        end
    end

    if action.op == OP_SWITCH
        if state.character == CHAR_ALICE
            new_state.character = CHAR_BOB
        else
            new_state.character = CHAR_ALICE
        end
    end

    return new_state
end

function valid_initial_state(state::GameState, bad_design::Bool)
    if state.alice_location != LOC_WEST_ROOM && state.alice_location != LOC_EAST_ROOM
        return false
    end

    if state.bob_location != LOC_WEST_ROOM && state.bob_location != LOC_EAST_ROOM
        return false
    end

    if state.red_key_location != LOC_WEST_ROOM && state.red_key_location != LOC_EAST_ROOM
        return false
    end

    if state.blue_key_location != LOC_WEST_ROOM && state.blue_key_location != LOC_EAST_ROOM
        return false
    end

    if state.green_key_location != LOC_WEST_ROOM && state.green_key_location != LOC_EAST_ROOM
        return false
    end

    if !bad_design
        if state.alice_location == state.bob_location && state.green_key_location != state.alice_location
            return false
        end
    end

    return true
end

# Index-mapping code

function index_for_state(state::GameState)
    # Encode the state as an 11-bit number, then add 1
    index_zero = 0

    index_zero |= (state.green_key_location - CHAR_ALICE)

    index_zero <<= 2
    index_zero |= (state.blue_key_location - CHAR_ALICE)

    index_zero <<= 2
    index_zero |= (state.red_key_location - CHAR_ALICE)

    index_zero <<= 2
    index_zero |= (state.bob_location - LOC_WEST_ROOM)

    index_zero <<= 2
    index_zero |= (state.alice_location - LOC_WEST_ROOM)

    index_zero <<= 1
    index_zero |= (state.character - CHAR_ALICE)

    return index_zero + 1
end

function state_for_index(index::Int)
    state = GameState(-1, -1, -1, -1, -1, -1)

    if index > GAME_STATES
        return state
    end

    index_zero = index - 1

    state.character = (index_zero & 0x01) + CHAR_ALICE
    index_zero >>= 1

    state.alice_location = (index_zero & 0x03) + LOC_WEST_ROOM
    index_zero >>= 2

    state.bob_location = (index_zero & 0x03) + LOC_WEST_ROOM
    index_zero >>= 2

    state.red_key_location = (index_zero & 0x03) + CHAR_ALICE
    index_zero >>= 2

    state.blue_key_location = (index_zero & 0x03) + CHAR_ALICE
    index_zero >>= 2

    state.green_key_location = (index_zero & 0x03) + CHAR_ALICE
    index_zero >>= 2

    return state
end

function valid_initial_index(i::Integer, bad_design::Bool)
    return valid_initial_state(state_for_index(i), bad_design)
end

# Analysis code

function fill_transition_matrix(matrix::AbstractArray{Float64,2}, bad_design::Bool, indexes::Array{Integer})
    # Normal transitions
    for i=1:(size(matrix,1)-1)
        state = state_for_index(i)
        actions = query_actions(state)
        for j=1:length(actions)
            if actions[j].op == OP_FINISH
                matrix[i,size(matrix,2)] += 1.0/length(actions)
            else
                new_state = apply_action(state, actions[j], bad_design)
                matrix[i,index_for_state(new_state)] += 1.0/length(actions)
            end
        end
    end

    # Game over
    for i=1:length(indexes)
        matrix[size(matrix,1),indexes[i]] = 1.0/length(indexes)
    end
end

function count_unit_eigenvalues(transition_matrix::AbstractArray{Float64,2})
    levalues = eigvals(transition_matrix')
    count = 0
    for i=1:length(levalues)
        if abs(levalues[i] - 1.0) < 1e-9
            count += 1
        end
    end
    return count
end

for i=1:GAME_STATES
    @assert i == index_for_state(state_for_index(i))
end

function analyze_game(bad_setup::Bool, bad_move::Bool)
    transition_matrix1 = zeros(GAME_STATES+1, GAME_STATES+1)
    transition_matrix2 = zeros(GAME_STATES+1, GAME_STATES+1)

    initial_states = Array{Integer}(0)
    for i=1:GAME_STATES
        if valid_initial_index(i, bad_setup)
            push!(initial_states, i)
        end
    end

    fill_transition_matrix(transition_matrix1, bad_move, Integer[GAME_STATES+1])
    fill_transition_matrix(transition_matrix2, bad_move, initial_states)

    ev1 = count_unit_eigenvalues(transition_matrix1)
    ev2 = count_unit_eigenvalues(transition_matrix2)

    if ev1 == ev2
        println(" => ", ev1, " recurrent classes and no dead ends! Hooray!")
        println("   => Verifying the result...")
    else
        println(" => There is a dead end :-(")
        println("   => Calculating how bad it is...")
    end

    state_vector = zeros(GAME_STATES+1)
    for i=1:length(initial_states)
        state_vector[initial_states[i]] = 1.0/length(initial_states)
    end

    # Use the eigendecomposition to compute lim t->infty U*L^t*U^-1
    # Eigenvalues less than one will go to zero in the diagonal matrix
    revalues, revectors = eig(transition_matrix1; scale=false)

    diagonal_vector = zeros(GAME_STATES+1)
    for i=1:length(revalues)
        if abs(revalues[i] - 1.0) < 1e-9
            diagonal_vector[i] = 1.0
        end
    end

    println("   => Still calculating...") # The "division" is basically a matrix inversion
    p = revectors * diagm(diagonal_vector) / revectors

    final_state = real(p' * state_vector)

    @printf(" => This bug affects %.2f%% of button-mashing players\n", (1.0-final_state[GAME_STATES+1])*100)

    valid_states = Array{Integer}(0)
    t = transition_matrix1^20 # Approximation for p, which seems to have a lot of floating-point jitter
    for i=1:GAME_STATES
        if real(t[i,GAME_STATES+1]) > 1e-8
            push!(valid_states, i)
        end
    end

    println(" => Valid states: ", length(valid_states))

    t = eye(GAME_STATES+1)
    for i=1:20
        t *= transition_matrix1
        can_be_finished = true
        for j=1:length(valid_states)
            if t[valid_states[j],GAME_STATES+1] == 0
                can_be_finished = false
                break
            end
        end
        if can_be_finished
            println(" => MAX_FINISH_DEPTH: ", i)
            break
        end
    end
end

println("Scenario 1: Green-key bug and help-me bug")
analyze_game(true, true)

println("Scenario 2: Green-key bug only")
analyze_game(true, false)

println("Scenario 3: Help-me bug only")
analyze_game(false, true)

println("Scenario 4: No bugs (hopefully)")
analyze_game(false, false)
