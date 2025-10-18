import math, os, random, subprocess
from datetime import date, datetime, timedelta, time

# ================= PERSONALIZE =================
WEEKS = 53              # largura do grid do GitHub
VINE_AMPLITUDE = 2      # 1–3 dá um balanço bonito
VINE_BASE = 3           # 0=dom ... 6=sáb (3≈quarta)
STEM_COMMITS = (1, 2)   # intensidade do caule (deixe baixo pra destacar suas folhas reais)
COMMIT_HOUR = 12        # hora do carimbo
SEED = 77               # mude para variar o desenho
DRY_RUN = False         # True = só imprime as datas, não cria commits
# =================================================

random.seed(SEED)

def run_git(args, env=None):
    subprocess.run(args, check=True, env=env)

def env_with_dates(d: date, minute_offset: int = 0):
    stamp = datetime.combine(d, time(hour=COMMIT_HOUR, minute=minute_offset % 60))
    iso = stamp.strftime("%Y-%m-%dT%H:%M:%S")
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = iso
    env["GIT_COMMITTER_DATE"] = iso
    return env

# === ponto inicial do grid: domingo de 52 semanas atrás ===
today = date.today()
days_since_sunday = (today.weekday() + 1) % 7  # seg=0...dom=6
last_sunday = today - timedelta(days=days_since_sunday)
grid_start = last_sunday - timedelta(weeks=52)

def day_at(col, row):
    return grid_start + timedelta(weeks=col, days=row)

def col_of(d: date) -> int:
    days = (d - grid_start).days
    return max(0, min(WEEKS - 1, days // 7))

# === começar a partir de 1º de setembro do ano atual ===
sep1 = date(today.year, 9, 1)
start_col = col_of(sep1)

# safety: precisa estar dentro do repo
if not os.path.isdir(".git"):
    raise SystemExit("Execute dentro de um repositório git já inicializado.")

# gera o caule coluna a coluna, seguindo o tempo (esq -> dir)
for col in range(start_col, WEEKS):
    # curva suave
    row_float = VINE_BASE + VINE_AMPLITUDE * math.sin(col / 5.5)
    row = max(0, min(6, int(round(row_float))))
    d = day_at(col, row)

    # pula dias no futuro
    if d > today:
        continue

    # commits vazios fracos (caule)
    n = random.randint(*STEM_COMMITS)
    # “nó” um pouco mais forte de tempos em tempos
    if col % 13 == 0:
        n += 1

    if DRY_RUN:
        print(f"[dry] stem {d} x{n}")
        continue

    for i in range(n):
        env = env_with_dates(d, i)
        msg = f"stem {d.isoformat()} #{i+1}"
        run_git(["git", "commit", "--allow-empty", "-m", msg], env=env)

print("🌿 Caule criado. Agora: git push")
