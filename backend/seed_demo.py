"""Demo seeder for EKATVA. Run from backend/ with the API server up and matching already executed.
    python3 seed_demo.py
Safe to re-run: skips existing user/reviews; CNMC endpoint is fingerprint-based.
"""
import json, os, urllib.request, urllib.error

from app.db.database import SessionLocal
from app.core.permissions import Role
from app.models.user import User
from app.models.review import Review
from app.models.material import Material
from app.models.material_match import MaterialMatch

API = os.environ.get("API_URL", "http://localhost:8000/api")
EMAIL, PASSWORD = "reviewer@ekatva.demo", "Demo@12345"


def hash_pw(pw: str) -> str:
    try:
        from app.core import security
        for name in ("get_password_hash", "hash_password"):
            if hasattr(security, name):
                return getattr(security, name)(pw)
    except Exception:
        pass
    from pwdlib import PasswordHash
    from pwdlib.hashers.argon2 import Argon2Hasher
    return PasswordHash((Argon2Hasher(),)).hash(pw)


def g(obj, *names, default=None):
    for n in names:
        if hasattr(obj, n) and getattr(obj, n) is not None:
            return getattr(obj, n)
    return default


db = SessionLocal()

# 1. Reviewer user
user = db.query(User).filter(User.email == EMAIL).first()
if not user:
    user = User(
        employee_id="EMP-DEMO-001", name="Demo Reviewer", email=EMAIL,
        password_hash=hash_pw(PASSWORD), role=Role.MATERIAL_REVIEWER.value,
        department="National Catalogue Cell", is_active=True,
    )
    db.add(user)
    db.commit()
    print("created user", EMAIL)
else:
    print("user exists")

# 2. Reviews from existing matches
matches = db.query(MaterialMatch).limit(40).all()
print("matches found:", len(matches))
existing = {r.match_id for r in db.query(Review.match_id).all()}
made = 0
for m in matches:
    if str(m.id) in existing:
        continue
    conflict = bool(g(m, "has_critical_conflict", default=False))
    score = g(m, "final_score", "overall_score", "score", "similarity_score")
    db.add(Review(
        match_id=str(m.id),
        status="PENDING",
        priority="CRITICAL" if conflict else ("HIGH" if score and score < 0.8 else "NORMAL"),
        original_ai_classification=str(g(m, "classification", "match_classification", default="REVIEW_REQUIRED")),
        ai_confidence=float(score) if score is not None else None,
        has_critical_conflict=conflict,
    ))
    made += 1
db.commit()
print("reviews created:", made)

# 3. CNMCs via API (clusters from strong matches, else single materials)
clusters = []
for m in matches:
    cls = str(g(m, "classification", "match_classification", default=""))
    a = g(m, "source_material_id", "material_a_id")
    b = g(m, "target_material_id", "material_b_id")
    if a and b and cls in ("IDENTICAL", "NEAR_DUPLICATE"):
        clusters.append([a, b])
    if len(clusters) >= 10:
        break
if len(clusters) < 10:
    for mat in db.query(Material).limit(10 - len(clusters)).all():
        clusters.append([mat.id])

ok = 0
for ids in clusters:
    req = urllib.request.Request(
        f"{API}/cnmc",
        data=json.dumps({"material_ids": ids}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=60)
        ok += 1
    except urllib.error.HTTPError as e:
        print("CNMC failed", ids, e.code, e.read()[:300])
    except Exception as e:
        print("CNMC failed", ids, e)
print("cnmc requests ok:", ok, "/", len(clusters))
print("Login:", EMAIL, "/", PASSWORD)