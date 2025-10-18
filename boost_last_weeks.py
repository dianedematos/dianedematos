import os, subprocess
from datetime import date, datetime, timedelta, time

COMMIT_HOUR = 12
EXTRA_PER_DAY = 4   # tente 4–6 se quiser bem escuro
DAYS = 18           # últimos N dias

def env_for(d, i):
    iso = datetime.combine(d, time(hour=COMMIT_HOUR, minute=i%60)).strftime("%Y-%m-%dT%H:%M:%S")
    e = os.environ.copy()
    e["GIT_AUTHOR_DATE"] = iso
    e["GIT_COMMITTER_DATE"] = iso
    return e

today = date.today()
for delta in range(DAYS):
    d = today - timedelta(days=delta)
    for i in range(EXTRA_PER_DAY):
        subprocess.run(["git","commit","--allow-empty","-m",f"boost {d} #{i+1}"], check=True, env=env_for(d,i))
print("Boost ok. Agora: git push")
