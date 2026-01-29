from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

ONE_REP_MAXES = {"squat_1rm": 180, "bench_1rm": 120, "deadlift_1rm": 220, "ohp_1rm": 80}


def test_ul_2day_general_fitness():
    payload = {
        "training_goal": "general_fitness",
        "available_days": ["monday", "thursday"],
        "session_duration_minutes": 60,
        "equipment": ["barbell", "dumbbell", "machine", "bodyweight"],
        "one_rep_maxes": ONE_REP_MAXES,
    }
    res = client.post("/generate-plan", json=payload)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    plan = res.json()
    print("\nUL 2day general_fitness:\n", plan)
    assert plan["inferred_split"]["monday"] == "upper"
    assert plan["inferred_split"]["thursday"] == "lower"


def test_ul_2day_strength():
    payload = {
        "training_goal": "strength",
        "available_days": ["monday", "thursday"],
        "session_duration_minutes": 75,
        "equipment": ["barbell", "dumbbell", "machine"],
        "one_rep_maxes": ONE_REP_MAXES,
        "required_primary_lifts": ["squat_1rm", "deadlift_1rm", "bench_1rm"],
    }
    res = client.post("/generate-plan", json=payload)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    plan = res.json()
    print("\nUL 2day strength:\n", plan)
    assert plan["inferred_split"]["monday"] == "upper"
    assert plan["inferred_split"]["thursday"] == "lower"


def test_ul_2day_hypertrophy():
    payload = {
        "training_goal": "hypertrophy",
        "available_days": ["monday", "thursday"],
        "session_duration_minutes": 60,
        "equipment": ["barbell", "dumbbell", "machine", "bodyweight"],
        "one_rep_maxes": ONE_REP_MAXES,
    }
    res = client.post("/generate-plan", json=payload)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    plan = res.json()
    print("\nUL 2day hypertrophy:\n", plan)
    assert plan["inferred_split"]["monday"] == "upper"
    assert plan["inferred_split"]["thursday"] == "lower"


def test_ul_bodyweight_2day_general_fitness_30min():
    payload = {
        "training_goal": "general_fitness",
        "available_days": ["monday", "thursday"],
        "session_duration_minutes": 30,
        "equipment": ["bodyweight"],
        "one_rep_maxes": ONE_REP_MAXES,
    }
    res = client.post("/generate-plan", json=payload)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    plan = res.json()
    print("\nUL bodyweight 2day general_fitness 30min:\n", plan)
    assert plan["inferred_split"]["monday"] == "upper"
    assert plan["inferred_split"]["thursday"] == "lower"


def test_ul_bodyweight_2day_strength_30min():
    payload = {
        "training_goal": "strength",
        "available_days": ["monday", "thursday"],
        "session_duration_minutes": 30,
        "equipment": ["bodyweight"],
        "one_rep_maxes": ONE_REP_MAXES,
        "include_cardio": True,
    }
    res = client.post("/generate-plan", json=payload)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    plan = res.json()
    print("\nUL bodyweight 2day strength 30min:\n", plan)
    assert plan["inferred_split"]["monday"] == "upper"
    assert plan["inferred_split"]["thursday"] == "lower"


def test_ulul_4day_hypertrophy():
    payload = {
        "training_goal": "hypertrophy",
        "available_days": ["monday", "tuesday", "thursday", "friday"],
        "session_duration_minutes": 60,
        "equipment": ["barbell", "dumbbell", "machine"],
        "one_rep_maxes": ONE_REP_MAXES,
    }
    res = client.post("/generate-plan", json=payload)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    plan = res.json()
    print("\nULUL 4day hypertrophy:\n", plan)
    assert plan["inferred_split"]["monday"] == "upper"
    assert plan["inferred_split"]["tuesday"] == "lower"
    assert plan["inferred_split"]["thursday"] == "upper"
    assert plan["inferred_split"]["friday"] == "lower"


def test_ulul_4day_strength():
    payload = {
        "training_goal": "strength",
        "available_days": ["monday", "tuesday", "thursday", "friday"],
        "session_duration_minutes": 75,
        "equipment": ["barbell", "dumbbell", "machine"],
        "one_rep_maxes": ONE_REP_MAXES,
        "required_primary_lifts": ["squat_1rm", "deadlift_1rm", "bench_1rm"],
    }
    res = client.post("/generate-plan", json=payload)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    plan = res.json()
    print("\nULUL 4day strength:\n", plan)
    assert plan["inferred_split"]["monday"] == "upper"
    assert plan["inferred_split"]["tuesday"] == "lower"
    assert plan["inferred_split"]["thursday"] == "upper"
    assert plan["inferred_split"]["friday"] == "lower"

