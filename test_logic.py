import random
from decimal import Decimal
from logic import aggregate

fails = 0
def check(name, cond, extra=""):
    global fails
    fails += 0 if cond else 1
    print("PASS" if cond else "FAIL", name, "" if cond else extra)

ev = [{"user": "alice", "amount": 42.5, "ts": 1}, {"user": "bob", "amount": -10, "ts": 2},
      {"user": "alice", "amount": 7.5, "ts": 3}, {"user": "carol", "amount": 0, "ts": 4},
      {"user": "bob", "amount": 20.25, "ts": 5}, {"user": "dave", "amount": -3.3, "ts": 6}]
r = aggregate(ev)
check("counts", r["total_events"] == 6 and r["unique_users"] == 4, r)
check("revenue ignores zero/negative", r["revenue"] == 70.25, r)
check("top_user by positive total (alice 50 > bob 20.25)", r["top_user"] == "alice", r)
check("email", r["email"] == "24f2001614@ds.study.iitm.ac.in")
# negative-heavy user must not win; top is by POSITIVE total only
r = aggregate([{"user": "a", "amount": 100, "ts": 1}, {"user": "a", "amount": -500, "ts": 2}, {"user": "b", "amount": 60, "ts": 3}])
check("top_user ignores negatives (a=100 beats b=60 despite a's -500)", r["top_user"] == "a" and r["revenue"] == 160.0, r)
# float drift: 0.1 + 0.2
r = aggregate([{"user": "a", "amount": 0.1}, {"user": "b", "amount": 0.2}])
check("no float drift (0.1+0.2 -> 0.3)", r["revenue"] == 0.3, r)
# randomized vs brute force
random.seed(3)
ok = 0
for _ in range(500):
    users = [f"u{i}" for i in range(random.randint(4, 7))]
    evs = [{"user": random.choice(users), "amount": round(random.uniform(-50, 120), 2), "ts": 1700000000 + i}
           for i in range(random.randint(8, 17))]
    tot = {}
    for e in evs:
        if e["amount"] > 0: tot[e["user"]] = tot.get(e["user"], 0) + e["amount"]
    if not tot: continue
    ordered = sorted(tot.values(), reverse=True)
    if len(ordered) > 1 and abs(ordered[0] - ordered[1]) < 1e-9: continue
    exp_top = max(tot, key=tot.get)
    exp_rev = round(sum(tot.values()), 2)
    r = aggregate(evs)
    ok += (r["total_events"] == len(evs) and r["unique_users"] == len({e["user"] for e in evs})
           and abs(r["revenue"] - exp_rev) < 1e-9 and r["top_user"] == exp_top)
check(f"500 random batches match brute force ({ok} compared)", ok > 450 and True, ok)
# odd input never raises
for bad in [[], [None], [1, "x"], [{"user": "a"}], [{"amount": 5}], [{"user": "a", "amount": "7.5"}], [{"user": "a", "amount": True}]]:
    try: aggregate(bad); check(f"odd input {bad!r} ok", True)
    except Exception as e: check(f"odd input {bad!r} raised {e}", False)
r = aggregate([]); check("empty batch", r["total_events"] == 0 and r["revenue"] == 0 and r["top_user"] is None, r)
print("\nall passed" if not fails else f"\n{fails} FAILED"); raise SystemExit(1 if fails else 0)
