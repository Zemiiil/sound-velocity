import sys
import glob
import os
import numpy as np
import matplotlib.pyplot as plt
import soundFunctions as s

dataPath = sys.argv[1] if len(sys.argv) > 1 else "sound/data/"
plotsPath = "sound/plots/"

L = 1.158

t, rh = s.readConditions(dataPath + "conditions.txt")
print("t = %.1f C, rh = %d %%" % (t, rh))

co2, speedRoom = s.speedOfSound(t, s.h2oFraction(t, rh), 5)
co2, speedWet = s.speedOfSound(t, s.h2oFraction(t, 100), 5)

fitRoom = np.polyfit(speedRoom, co2, 1)
fitWet = np.polyfit(speedWet, co2, 1)
print("Прямая, влажность аудитории:", fitRoom)
print("Прямая, влажность 100 %:", fitWet)


def delays(prefix):
    taus = []
    for file0 in sorted(glob.glob(dataPath + prefix + "*_0.txt")):
        name = os.path.basename(file0)[:-len("_0.txt")]
        mic0 = np.loadtxt(dataPath + name + "_0.txt")
        mic1 = np.loadtxt(dataPath + name + "_1.txt")
        N, tau = s.findDelay(mic0, mic1)
        print("%-8s N = %d, tau = %.3f мс" % (name, N, tau))
        taus.append(tau)
    return np.array(taus)


tauAir = delays("air")
tauBreath = delays("breath")

cAir = L / (np.mean(tauAir) / 1000)
cBreath = L / (np.mean(tauBreath) / 1000)

co2Air = np.polyval(fitRoom, cAir)
co2Breath = np.polyval(fitWet, cBreath)

print("Воздух: c = %.1f м/с, CO2 = %.1f %%" % (cAir, co2Air))
print("Выдох:  c = %.1f м/с, CO2 = %.1f %%" % (cBreath, co2Breath))

for label, taus, fit in [("Воздух", tauAir, fitRoom), ("Выдох", tauBreath, fitWet)]:
    if len(taus) > 1:
        dTau = np.std(taus, ddof=1) / np.sqrt(len(taus))
        c = L / (np.mean(taus) / 1000)
        dC = c * dTau / np.mean(taus)
        print("%s: dtau = %.4f мс, dc = %.2f м/с, dCO2 = %.1f %%" % (label, dTau, dC, abs(fit[0]) * dC))

eta = (co2Breath / 100 - 0.0003) / 0.2095
print("Доля усвоенного кислорода: %.2f" % eta)

plt.plot(co2, speedRoom, label="влажность %d %%" % rh)
plt.plot(co2, speedWet, label="влажность 100 %")
plt.plot(co2Air, cAir, "*", markersize=14, label="Воздух: %.1f м/с, %.1f %%" % (cAir, co2Air))
plt.plot(co2Breath, cBreath, "*", markersize=14, label="Выдох: %.1f м/с, %.1f %%" % (cBreath, co2Breath))
plt.xlabel("Доля CO₂ в сухом воздухе, %")
plt.ylabel("Скорость звука, м/с")
plt.grid()
plt.legend()
plt.savefig(plotsPath + "speed-of-sound.png", dpi=150)
plt.show()
