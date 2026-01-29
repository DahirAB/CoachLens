from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

ONE_REP_MAXES = {"squat_1rm": 180, "bench_1rm": 120, "deadlift_1rm": 220, "ohp_1rm": 80}


def test_ppl_strength_3day():
    payload = {
        "training_goal": "strength",
        "available_days": ["monday", "wednesday", "friday"],
        "session_duration_minutes": 60,
        "equipment": ["barbell", "dumbbell", "machine"],
        "one_rep_maxes": ONE_REP_MAXES,
        "required_primary_lifts": ["squat_1rm", "deadlift_1rm"],
    }
    res = client.post("/generate-plan", json=payload)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    plan = res.json()
    print("\nPPL strength 3day:\n", plan)
    assert plan["inferred_split"]["monday"] == "push"
    assert plan["inferred_split"]["wednesday"] == "pull"
    assert plan["inferred_split"]["friday"] == "legs"


def test_ppl_hypertrophy_3day():
    payload = {
        "training_goal": "hypertrophy",
        "available_days": ["monday", "wednesday", "friday"],
        "session_duration_minutes": 60,
        "equipment": ["barbell", "dumbbell", "machine", "bodyweight"],
        "one_rep_maxes": ONE_REP_MAXES,
    }
    res = client.post("/generate-plan", json=payload)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    plan = res.json()
    print("\nPPL hypertrophy 3day:\n", plan)
    assert plan["inferred_split"]["monday"] == "push"
    assert plan["inferred_split"]["wednesday"] == "pull"
    assert plan["inferred_split"]["friday"] == "legs"


def test_ppl_fat_loss_3day_include_cardio():
    payload = {
        "training_goal": "fat_loss",
        "available_days": ["monday", "wednesday", "friday"],
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
    print("\nPPL fat_loss 3day include_cardio:\n", plan)
    assert plan["inferred_split"]["monday"] == "push"
    assert plan["inferred_split"]["wednesday"] == "pull"
    assert plan["inferred_split"]["friday"] == "legs"


def test_ppl_bodyweight_hypertrophy_30min():
    payload = {
        "training_goal": "hypertrophy",
        "available_days": ["monday", "wednesday", "friday"],
        "session_duration_minutes": 30,
        "equipment": ["bodyweight"],
        "one_rep_maxes": ONE_REP_MAXES,
    }
    res = client.post("/generate-plan", json=payload)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    plan = res.json()
    print("\nPPL bodyweight hypertrophy 30min:\n", plan)
    assert plan["inferred_split"]["monday"] == "push"
    assert plan["inferred_split"]["wednesday"] == "pull"
    assert plan["inferred_split"]["friday"] == "legs"


def test_ppl_bodyweight_strength_30min():
    payload = {
        "training_goal": "strength",
        "available_days": ["monday", "wednesday", "friday"],
        "session_duration_minutes": 30,
        "equipment": ["bodyweight"],
        "one_rep_maxes": ONE_REP_MAXES,
    }
    res = client.post("/generate-plan", json=payload)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    plan = res.json()
    print("\nPPL bodyweight strength 30min:\n", plan)
    assert plan["inferred_split"]["monday"] == "push"
    assert plan["inferred_split"]["wednesday"] == "pull"
    assert plan["inferred_split"]["friday"] == "legs"


def test_ppl_bodyweight_fat_loss_60min_include_cardio():
    payload = {
        "training_goal": "fat_loss",
        "available_days": ["monday", "wednesday", "friday"],
        "session_duration_minutes": 60,
        "equipment": ["bodyweight"],
        "one_rep_maxes": ONE_REP_MAXES,
        "include_cardio": True,
    }
    res = client.post("/generate-plan", json=payload)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    plan = res.json()
    print("\nPPL bodyweight fat_loss 60min include_cardio:\n", plan)
    assert plan["inferred_split"]["monday"] == "push"
    assert plan["inferred_split"]["wednesday"] == "pull"
    assert plan["inferred_split"]["friday"] == "legs"


def test_ppl_x2_6day():
    payload = {
        "training_goal": "hypertrophy",
        "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"],
        "session_duration_minutes": 60,
        "equipment": ["barbell", "dumbbell", "machine"],
        "one_rep_maxes": ONE_REP_MAXES,
    }
    res = client.post("/generate-plan", json=payload)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    plan = res.json()
    print("\nPPL x2 6day:\n", plan)
    assert plan["inferred_split"]["monday"] == "push"
    assert plan["inferred_split"]["tuesday"] == "pull"
    assert plan["inferred_split"]["wednesday"] == "legs"
    assert plan["inferred_split"]["thursday"] == "push"
    assert plan["inferred_split"]["friday"] == "pull"
    assert plan["inferred_split"]["saturday"] == "legs"

