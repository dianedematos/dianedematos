import math
import os
import random
import subprocess
import sys
from datetime import date, datetime, timedelta, time

# ================= PERSONALIZE =================
START_MONTH = 9          # começa em setembro (9)
VINE_BASE = 3            # 0=dom ... 6=sáb (3≈quarta)
VINE_AMPLITUDE = 2       # "balanço" do caule (1–3)
STEM_COMMITS = (1, 2)    # intensidade do caule (mantém discreto)
KNOT_EVERY = 13          # nózinho mais escuro a cada N colunas
BRANCH_EVERY = 7         # a cada N colunas cria micro-ramo
BRANCH_HEIGHT = 2        # quantas linhas o ramo sobe/desce
BLOSSOM_SIZE = 2         # quantas colunas finais concentram "flor"
BLOSSOM_EXTRA = 2        # commits extras em cada ponto da flor
COMMIT_HOUR = 12         # hora dos carimbos
SEED = 1229              # mude para variar o desenho
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

# ==== Grid do GitHub (53 semanas x 7 dias) ====
WEEKS = 53
today = date.today()
days_since_sunday = (today.weekday() + 1) % 7  # seg=0...dom=6
last_sunday = today - timedelta(days=days_since_sunday)
grid_start = last_sunday - timedelta(weeks=52)

def day_at(col, row):
    return grid_start + timedelta(weeks=col, days=row)

def col_of(d: date) -> int:
    days = (d - grid_start).days
    return max(0, min(WEEKS - 1, days // 7))

# === coluna inicial: 1º de setembro do ano atual ===
sep1 = date(today.year, START_MONTH, 1)
start_col = col_of(sep1)

def stem_row(col: int) -> int:
    """Curva principal do caule."""
    row_float = VINE_BASE + VINE_AMPLITUDE * math.sin(col / 5.5)
    return max(0, min(6, int(round(row_float))))

def commit_empty_on(d: date, n: int, label="stem"):
    for i in range(n):
        env = env_with_dates(d, i)
        msg = f"{label} {d.isoformat()} #{i+1}"
        run_git(["git", "commit", "--allow-empty", "-m", msg], env=env)

def make_stem_and_branches(dry=False):
    """Desenha o caule + pequenos ramos (commits vazios)."""
    for col in range(start_col, WEEKS):
        d = day_at(col, stem_row(col))
        if d > today:
            break

        # caule básico
        n = random.randint(*STEM_COMMITS)
        if col % KNOT_EVERY == 0:
            n += 1  # nózinho mais escuro
        if dry:
            print(f"[dry] stem {d} x{n}")
        else:
            commit_empty_on(d, n, label="stem")

        # ramo suave (ziguezague curto)
        if col % BRANCH_EVERY == 0:
            for sign in (-1, 1):
                r = stem_row(col) + sign * min(BRANCH_HEIGHT, 6)
                r = max(0, min(6, r))
                d_branch = day_at(col, r)
                if d_branch > today:
                    continue
                if dry:
                    print(f"[dry] branch {d_branch} x1")
                else:
                    commit_empty_on(d_branch, 1, label="branch")

    # “flor” no final: cluster mais escuro nas últimas colunas válidas
    last_col = min(col_of(today), WEEKS - 1)
    for c in range(max(start_col, last_col - BLOSSOM_SIZE + 1), last_col + 1):
        center_row = stem_row(c)
        for r in [center_row, max(0, center_row - 1), min(6, center_row + 1)]:
            d = day_at(c, r)
            if d > today:
                continue
            n = random.randint(*STEM_COMMITS) + BLOSSOM_EXTRA
            if dry:
                print(f"[dry] blossom {d} x{n}")
            else:
                commit_empty_on(d, n, label="blossom")

def plan_real_leaves(days_ahead=21):
    """Imprime dias ideais (próximas semanas) para commits reais (folhas)."""
    print("\n🍃  SUGESTÕES DE DIAS PARA 'FOLHAS' (commits reais):")
    start = today
    end = today + timedelta(days=days_ahead)
    col_start = col_of(start)
    col_end = min(WEEKS - 1, col_of(end))
    rows = ["Dom","Seg","Ter","Qua","Qui","Sex","Sáb"]
    tips = []
    for c in range(col_start, col_end + 1):
        d_stem = day_at(c, stem_row(c))
        if d_stem < start or d_stem > end:
            continue
        # bons lugares: vizinhos ao caule (acima/abaixo) + ponto de ramo
        candidates = set()
        candidates.add((c, max(0, stem_row(c) - 1)))
        candidates.add((c, min(6, stem_row(c) + 1)))
        if c % BRANCH_EVERY == 0:
            candidates.add((c, max(0, stem_row(c) - BRANCH_HEIGHT)))
            candidates.add((c, min(6, stem_row(c) + BRANCH_HEIGHT)))
        for (cc, rr) in sorted(candidates):
            d = day_at(cc, rr)
            if start <= d <= end:
                tips.append((d, rows[rr]))
    tips = sorted(set(tips))
    for d, rowname in tips:
        print(f"  - {d.isoformat()} ({rowname}) → faça 1–3 commits reais (README, imagens, docs)")

def main():
    mode = (sys.argv[1].lower() if len(sys.argv) > 1 else "commit").strip()
    if not os.path.isdir(".git"):
        raise SystemExit("⚠️ Rode dentro de um repositório git já inicializado.")
    if mode == "plan":
        plan_real_leaves(21)
        return
    if mode == "dry":
        make_stem_and_branches(dry=True)
        return
    if mode == "commit":
        make_stem_and_branches(dry=False)
        print("\n🌿 Caule+ramificações+flor criados. Agora: git push")
        return
    raise SystemExit("Use: python vine_organic.py [commit|plan|dry]")

if __name__ == "__main__":
    main()
