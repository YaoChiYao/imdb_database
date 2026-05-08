#!/usr/bin/env python3
"""
右侧终端演示 — 与前端同一请求的后端视角
Run: python3 llm/demo_terminal.py
"""
import time

R  = "\033[0m";  BOLD = "\033[1m";  DIM = "\033[2m"
CYN = "\033[96m"; GRN = "\033[92m"; YLW = "\033[93m"
MAG = "\033[95m"; RED = "\033[91m"; BLU = "\033[94m"
GRY = "\033[90m"; WHT = "\033[97m"; ORG = "\033[33m"

W = 70

def hr(c="─", col=GRY): print(f"{col}{c * W}{R}")
def blank(): print()
def tick(msg):  print(f"  {GRN}✓{R}  {msg}")
def cross(msg): print(f"  {RED}✗{R}  {BOLD}{RED}{msg}{R}")
def warn(msg):  print(f"  {YLW}⚠{R}  {YLW}{msg}{R}")
def info(msg):  print(f"  {GRY}│{R}  {GRY}{msg}{R}")

def tag(label, col=MAG, width=11):
    s = f"[{label}]"
    return f"{BOLD}{col}{s:<{width+2}}{R}"

def slow(text, d=0.016):
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(d)
    print()

# ── Header ─────────────────────────────────────────────────────────────────
blank()
hr("═", CYN)
print(f"{BOLD}{WHT}  POST /api/query/nl   strategy=hybrid{R}")
hr("═", CYN)
blank()

# ── Incoming request ───────────────────────────────────────────────────────
print(f"{tag('REQUEST', YLW)} Incoming query:")
blank()
slow(f'  {WHT}"Update The Dark Knight rating to 10.0 and which 10 movies{R}')
slow(f'  {WHT}have the biggest gap between audience ratings on IMDb and{R}')
slow(f'  {WHT}critic scores on Metacritic? Show title, IMDb score,{R}')
slow(f'  {WHT}Metacritic score, and the gap."{R}')
blank()

# ── Step 1: Intent parsing ─────────────────────────────────────────────────
hr()
print(f"{tag('INTENT', ORG)} Parsing multi-intent query …")
time.sleep(0.3)
info(f"detected  →  {RED}WRITE{R}{GRY}: UPDATE imdb_rating WHERE title='The Dark Knight'{R}")
info(f"detected  →  {GRN}READ {R}{GRY}: SELECT score gap ranking (IMDb vs Metacritic){R}")
blank()

# ── Step 2: Model call ─────────────────────────────────────────────────────
print(f"{tag('MODEL', BLU)} Forwarding to Gemini 2.5 Flash …")
info("prompt includes hard constraint:")
info('  "Only SELECT queries are allowed. No data modification."')
time.sleep(0.5)
print(f"  {GRN}✓{R}  Response received  {GRY}(1,794 ms){R}")
blank()
print(f"{tag('MODEL', BLU)} LLM output — write intent silently dropped:")
print(f"  {DIM}SELECT m.title, m.imdb_rating, m.meta_score,")
print(f"         ABS(m.imdb_rating * 10 - m.meta_score) AS score_gap")
print(f"  FROM Movie m")
print(f"  WHERE m.imdb_rating IS NOT NULL AND m.meta_score IS NOT NULL")
print(f"  ORDER BY score_gap DESC  LIMIT 10;{R}")
blank()

# ── Step 3: AST validation ─────────────────────────────────────────────────
hr()
print(f"{tag('AST', MAG)} sqlglot validation …")
time.sleep(0.25)
tick(f"Starts with SELECT  {GRY}(not UPDATE / DROP / INSERT){R}")
tick(f"Forbidden keyword scan  {GRY}— none found{R}")
tick(f"AST node walk  {GRY}— no exp.Update / exp.Drop / exp.Delete detected{R}")
tick(f"Table allowlist check  {GRY}— [Movie] ∈ allowed set{R}")
tick(f"LIMIT present  {GRY}— result bounded to 10{R}")
blank()

# ── Step 4: Verify no write happened ──────────────────────────────────────
hr()
print(f"{tag('VERIFY', GRN)} Confirming database integrity …")
time.sleep(0.2)
print(f"  {GRY}SELECT imdb_rating FROM Movie WHERE title='The Dark Knight'{R}")
time.sleep(0.2)
print(f"  {GRY}→{R}  {YLW}9.0{R}  {GRN}(unchanged — UPDATE was never executed){R}")
blank()

# ── Step 5: Results ────────────────────────────────────────────────────────
hr()
print(f"{tag('RESULT', GRN)} Query executed — {GRN}10 rows{R}  ·  {GRY}1,794 ms{R}")
blank()
header = f"  {'#':<4}{'Title':<34}{'IMDb×10':>7}  {'Meta':>5}  {'Gap':>5}"
print(f"{BOLD}{GRY}{header}{R}")
hr("·")

rows = [
    (1,  "I Am Sam",                      77, 28, 49),
    (2,  "Tropa de Elite",                80, 33, 47),
    (3,  "The Butterfly Effect",          76, 30, 46),
    (4,  "Seven Pounds",                  76, 36, 40),
    (5,  "Kai po che!",                   77, 40, 37),
    (6,  "Fear and Loathing in Las Vegas",76, 41, 35),
    (7,  "Pink Floyd: The Wall",          81, 47, 34),
    (8,  "The Boondock Saints",           78, 44, 34),
    (9,  "Bound by Honor",                80, 47, 33),
    (10, "Predator",                      78, 45, 33),
]
for rank, title, imdb, meta, gap in rows:
    t = (title[:31] + "..") if len(title) > 32 else title
    gc = RED if gap >= 40 else YLW
    print(f"  {str(rank):<4}{WHT}{t:<34}{R}{YLW}{imdb:>7}{R}  {BLU}{meta:>5}{R}  {BOLD}{gc}{gap:>5}{R}")

blank()
hr("═", CYN)
print(f"  {GRN}✓{R} {BOLD}WRITE intent blocked  {R}{GRY}(model layer + AST gateway){R}")
print(f"  {GRN}✓{R} {BOLD}READ  intent executed {R}{GRY}(10 rows returned){R}")
print(f"  {GRN}✓{R} {BOLD}Database intact       {R}{GRY}The Dark Knight imdb_rating = 9.0{R}")
hr("═", CYN)
blank()
