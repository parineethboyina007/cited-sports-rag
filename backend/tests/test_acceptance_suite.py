import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def test_app():
    with TestClient(app) as c:
        yield c


def test_1_multi_medal_correctness(test_app):
    resp = test_app.post("/api/query", json={"query": "How many Olympic medals has Neeraj Chopra won, and where?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "OLY-001" in data["citations"]
    ans = data["answer"].lower()
    assert "gold" in ans and "tokyo 2020" in ans
    assert "silver" in ans and "paris 2024" in ans


def test_2_4way_surname_collision(test_app):
    resp = test_app.post("/api/query", json={"query": "Tell me about Khan."})
    assert resp.status_code == 200
    data = resp.json()
    assert data["collision_detected"] is True
    ans = data["answer"]
    assert "Zaheer Khan" in ans
    assert "Imran Khan" in ans
    assert "Younis Khan" in ans
    assert "Rashid Khan" in ans


def test_3_twin_siblings(test_app):
    resp = test_app.post("/api/query", json={"query": "Compare Steve Waugh and Mark Waugh."})
    assert resp.status_code == 200
    data = resp.json()
    citations = data["citations"]
    assert "CRI-006" in citations
    assert "CRI-015" in citations


def test_4_same_surname_different_generation(test_app):
    resp = test_app.post("/api/query", json={"query": "What did Shahid Afridi and Shaheen Afridi each achieve?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "CRI-068" in data["citations"]
    assert "CRI-078" in data["citations"]


def test_5_core_cross_dataset(test_app):
    resp = test_app.post("/api/query", json={"query": "Tell me about Kumar."})
    assert resp.status_code == 200
    data = resp.json()
    ans = data["answer"]
    assert data["collision_detected"] is True
    assert "Kumar Sangakkara" in ans
    assert "Sushil Kumar" in ans
    assert "Ravi Kumar Dahiya" in ans
    assert "Vijay Kumar" in ans


def test_6_largest_collision(test_app):
    resp = test_app.post("/api/query", json={"query": "Tell me about Singh."})
    assert resp.status_code == 200
    data = resp.json()
    ans = data["answer"]
    assert data["collision_detected"] is True
    assert "Yuvraj Singh" in ans
    assert "Harbhajan Singh" in ans
    assert "Bishan Singh Bedi" in ans
    assert "Sarabjot Singh" in ans
    assert "Milkha Singh" in ans


def test_7_no_source_refusal_absent_entity(test_app):
    resp = test_app.post("/api/query", json={"query": "What is Rafael Nadal's Olympic medal record?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["method"] == "refusal"
    ans = data["answer"].lower()
    assert "don't have" in ans or "no" in ans


def test_8_tempting_to_fabricate_absent_attribute(test_app):
    resp = test_app.post("/api/query", json={"query": "What is Virat Kohli's net worth?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["method"] == "refusal"
    ans = data["answer"].lower()
    assert "net worth" in ans or "doesn't record" in ans or "not tracked" in ans
    assert "CRI-026" in data["answer"]


def test_9_resistance_to_parametric_leakage(test_app):
    resp = test_app.post("/api/query", json={"query": "What was Sachin Tendulkar's highest individual Test score?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["method"] == "refusal"


def test_10_structured_field_filter(test_app):
    resp = test_app.post("/api/query", json={"query": "List all Sri Lankan wicket-keeper batsmen in the dataset."})
    assert resp.status_code == 200
    data = resp.json()
    ans = data["answer"]
    assert "Kumar Sangakkara" in ans


def test_11_standard_1_to_1_pairing(test_app):
    resp = test_app.post("/api/query", json={"query": "Which Olympic athlete competed at both Beijing 2008 and London 2012?"})
    assert resp.status_code == 200
    data = resp.json()
    ans = data["answer"]
    assert "Sushil Kumar" in ans


def test_12_irregular_pairing_manu_bhaker(test_app):
    resp = test_app.post("/api/query", json={"query": "How many medals did Manu Bhaker win at Paris 2024, and what color?"})
    assert resp.status_code == 200
    data = resp.json()
    ans = data["answer"].lower()
    assert "bronze" in ans
    assert "OLY-004" in data["citations"]
