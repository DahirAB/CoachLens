from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

ONE_REP_MAXES = {"squat_1rm": 180, "bench_1rm": 120, "deadlift_1rm": 220, "ohp_1rm": 80}


def test_mixed_5day_strength_roles():
    payload = {
        "training_goal": "strength",
        "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
        "session_duration_minutes": 75,
        "equipment": ["barbell", "dumbbell", "machine", "bodyweight"],
        "one_rep_maxes": ONE_REP_MAXES,
        "required_primary_lifts": ["deadlift_1rm", "bench_1rm", "squat_1rm"],
    }
    res = client.post("/generate-plan", json=payload)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    plan = res.json()
    print("\nMIXED 5day strength:\n", plan)
    assert plan["inferred_split"]["monday"] == "push"
    assert plan["inferred_split"]["tuesday"] == "pull"
    assert plan["inferred_split"]["wednesday"] == "legs"
    assert plan["inferred_split"]["thursday"] == "upper"
    assert plan["inferred_split"]["friday"] == "lower"


def test_mixed_5day_hypertrophy_roles():
    payload = {
        "training_goal": "hypertrophy",
        "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
        "session_duration_minutes": 60,
        "equipment": ["barbell", "dumbbell", "machine", "bodyweight"],
        "one_rep_maxes": ONE_REP_MAXES,
    }
    res = client.post("/generate-plan", json=payload)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    plan = res.json()
    print("\nMIXED 5day hypertrophy:\n", plan)
    assert plan["inferred_split"]["monday"] == "push"
    assert plan["inferred_split"]["tuesday"] == "pull"
    assert plan["inferred_split"]["wednesday"] == "legs"
    assert plan["inferred_split"]["thursday"] == "upper"
    assert plan["inferred_split"]["friday"] == "lower"


def test_mixed_5day_general_fitness_include_cardio():
    payload = {
        "training_goal": "general_fitness",
        "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
        "session_duration_minutes": 60,
        "equipment": ["barbell", "dumbbell", "machine", "bodyweight"],
        "one_rep_maxes": ONE_REP_MAXES,
        "include_cardio": True,
    }
    res = client.post("/generate-plan", json=payload)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    plan = res.json()
    print("\nMIXED 5day general_fitness include_cardio:\n", plan)
    assert plan["inferred_split"]["monday"] == "push"
    assert plan["inferred_split"]["tuesday"] == "pull"
    assert plan["inferred_split"]["wednesday"] == "legs"
    assert plan["inferred_split"]["thursday"] == "upper"
    assert plan["inferred_split"]["friday"] == "lower"


def test_mixed_7day_general_fitness_has_full_body_day():
    payload = {
        "training_goal": "general_fitness",
        "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
        "session_duration_minutes": 45,
        "equipment": ["barbell", "dumbbell", "machine", "bodyweight"],
        "one_rep_maxes": ONE_REP_MAXES,
        "include_cardio": True,
    }
    res = client.post("/generate-plan", json=payload)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    plan = res.json()
    print("\nMIXED 7day general_fitness:\n", plan)
    assert plan["inferred_split"]["sunday"] == "full_body"


def test_mixed_7day_strength_has_full_body_day():
    payload = {
        "training_goal": "strength",
        "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
        "session_duration_minutes": 60,
        "equipment": ["barbell", "dumbbell", "machine", "bodyweight"],
        "one_rep_maxes": ONE_REP_MAXES,
        "required_primary_lifts": ["deadlift_1rm", "bench_1rm", "squat_1rm"],
    }
    res = client.post("/generate-plan", json=payload)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    plan = res.json()
    print("\nMIXED 7day strength:\n", plan)
    assert plan["inferred_split"]["sunday"] == "full_body"


def test_mixed_7day_bodyweight_strength_has_full_body_day():
    payload = {
        "training_goal": "strength",
        "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
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
    print("\nMIXED 7day bodyweight strength:\n", plan)
    assert plan["inferred_split"]["sunday"] == "full_body"

