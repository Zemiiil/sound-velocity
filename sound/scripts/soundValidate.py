import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import soundFunctions as s

dataPath = "sound/data/"
plotsPath = "sound/plots/"
NREF = 845
W0, W1 = 15, 460
NOISE = 2.0
TRIALS = 300
rng = np.random.default_rng(7)
plt.rcParams["font.size"] = 13


def fshift(x, d):
    ext = np.concatenate([x[::-1], x, x[::-1]])
    X = np.fft.rfft(ext - ext.mean())
    f = np.fft.rfftfreq(len(ext))
    y = np.fft.irfft(X * np.exp(-2j * np.pi * f * d), len(ext)) + ext.mean()
    return y[len(x):2 * len(x)]


lines = []
errs = {}
for name in ["test6", "test2", "breath1"]:
    b = np.loadtxt(dataPath + name + "_1.txt")
    e = []
    for _ in range(TRIALS):
        nTrue = NREF - 5 + 10 * rng.random()
        a = 0.7 * fshift(b, nTrue) + 120 + rng.normal(0, NOISE, len(b))
        bb = b + rng.normal(0, NOISE, len(b))
        N = s.findDelay(a, bb, NREF, W0, W1)[0]
        e.append(N - nTrue)
    errs[name] = np.array(e)
    lines.append("%s: смещение %+.3f отсчёта, СКО %.3f отсчёта = %.2f мкс" %
                 (name, np.mean(e), np.std(e), np.std(e) * s.DT * 1000))
print("\n".join(lines))
with open(plotsPath + "validation.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

fig, ax = plt.subplots(figsize=(8, 4.2))
for name, e in errs.items():
    ax.hist(e * s.DT * 1000, bins=30, alpha=0.6, label=name)
ax.set_xlabel("Ошибка найденной задержки, мкс")
ax.set_ylabel("Число испытаний")
ax.set_title("Проверка на синтетических данных: %d испытаний на запись" % TRIALS)
ax.legend()
ax.grid()
fig.tight_layout()
fig.savefig(plotsPath + "validation.png", dpi=150)
