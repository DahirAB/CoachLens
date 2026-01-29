from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

ONE_REP_MAXES = {"squat_1rm": 180, "bench_1rm": 120, "deadlift_1rm": 220, "ohp_1rm": 80}


def test_full_body_1day_general_fitness():
    payload = {
        "training_goal": "general_fitness",
        "available_days": ["saturday"],
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
    print("\nFULL_BODY 1day general_fitness:\n", plan)
    assert plan["inferred_split"]["saturday"] == "full_body"


def test_full_body_1day_strength():
    payload = {
        "training_goal": "strength",
        "available_days": ["saturday"],
        "session_duration_minutes": 60,
        "equipment": ["barbell", "dumbbell", "machine", "bodyweight"],
        "one_rep_maxes": ONE_REP_MAXES,
    }
    res = client.post("/generate-plan", json=payload)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    plan = res.json()
    print("\nFULL_BODY 1day strength:\n", plan)
    assert plan["inferred_split"]["saturday"] == "full_body"


def test_full_body_1day_bodyweight_general_fitness():
    payload = {
        "training_goal": "general_fitness",
        "available_days": ["saturday"],
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
    print("\nFULL_BODY 1day bodyweight general_fitness:\n", plan)
    assert plan["inferred_split"]["saturday"] == "full_body"

