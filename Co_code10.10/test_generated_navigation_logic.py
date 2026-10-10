from navigation_logic import decide_next_move

def test_1():
    state = {
        "goal_ahead": True,
        "goal_on_left": False,
        "goal_on_right": False,
        "front_blocked": False,
        "left_blocked": False,
        "right_blocked": False
    }
    assert decide_next_move(state) == "FORWARD"

def test_2():
    state = {
        "goal_ahead": False,
        "goal_on_left": True,
        "goal_on_right": False,
        "front_blocked": False,
        "left_blocked": False,
        "right_blocked": False
    }
    assert decide_next_move(state) == "LEFT"

def test_3():
    state = {
        "goal_ahead": False,
        "goal_on_left": False,
        "goal_on_right": True,
        "front_blocked": False,
        "left_blocked": False,
        "right_blocked": False
    }
    assert decide_next_move(state) == "RIGHT"

def test_4():
    state = {
        "goal_ahead": True,
        "goal_on_left": False,
        "goal_on_right": False,
        "front_blocked": True,
        "left_blocked": False,
        "right_blocked": False
    }
    assert decide_next_move(state) == "LEFT"

def test_5():
    state = {
        "goal_ahead": True,
        "goal_on_left": False,
        "goal_on_right": False,
        "front_blocked": True,
        "left_blocked": True,
        "right_blocked": False
    }
    assert decide_next_move(state) == "RIGHT"

def test_6():
    state = {
        "goal_ahead": False,
        "goal_on_left": True,
        "goal_on_right": False,
        "front_blocked": False,
        "left_blocked": True,
        "right_blocked": False
    }
    assert decide_next_move(state) == "FORWARD"

def test_7():
    state = {
        "goal_ahead": False,
        "goal_on_left": False,
        "goal_on_right": True,
        "front_blocked": False,
        "left_blocked": False,
        "right_blocked": True
    }
    assert decide_next_move(state) == "FORWARD"

def test_8():
    state = {
        "goal_ahead": False,
        "goal_on_left": False,
        "goal_on_right": False,
        "front_blocked": False,
        "left_blocked": False,
        "right_blocked": False
    }
    assert decide_next_move(state) == "FORWARD"

def test_9():
    state = {
        "goal_ahead": False,
        "goal_on_left": False,
        "goal_on_right": False,
        "front_blocked": True,
        "left_blocked": True,
        "right_blocked": True
    }
    assert decide_next_move(state) == "STOP"