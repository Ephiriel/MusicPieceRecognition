import matplotlib.pyplot as plt
import numpy as np
from midilibrary import MidiLibrary
from FingerPrinting import FingerPrinting


##################################
## TEST 1 TOP 5 Percent
x = [5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 25, 30]

sw_ranks = [0.257, 0.478, 0.710, 0.848, 0.901, 0.949, 0.975, 0.984, 0.983, 0.983, 0.988, 0.986, 0.988]
dtw_ranks = [0.232, 0.414, 0.580, 0.743, 0.844, 0.906, 0.961, 0.979, 0.986, 0.987, 0.989, 0.990, 0.990]
fp1_ranks = [0.612, 0.833, 0.931, 0.965, 0.977, 0.984, 0.987, 0.988, 0.990, 0.991, 0.992, 0.992, 0.992]
fp2_ranks = [0.338, 0.597, 0.768, 0.882, 0.939, 0.965, 0.986, 0.986, 0.987, 0.989, 0.990, 0.991, 0.993]
fp3_ranks = [0.376, 0.703, 0.852, 0.931, 0.965, 0.979, 0.985, 0.985, 0.989, 0.990, 0.990, 0.991, 0.992]
_95_line = [0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95]

_sw_top = [0.145, 0.315, 0.585, 0.750, 0.828, 0.902, 0.950, 0.970, 0.965, 0.968, 0.978, 0.973, 0.975]
dtw_top = [0.127, 0.285, 0.449, 0.632, 0.764, 0.845, 0.930, 0.960, 0.972, 0.975, 0.978, 0.979, 0.981]
fp1_top = [0.462, 0.738, 0.883, 0.935, 0.956, 0.969, 0.975, 0.976, 0.981, 0.983, 0.984, 0.984, 0.984]
fp2_top = [0.208, 0.462, 0.657, 0.809, 0.897, 0.936, 0.972, 0.973, 0.974, 0.977, 0.980, 0.983, 0.985]
fp3_top = [0.253, 0.592, 0.774, 0.884, 0.937, 0.960, 0.970, 0.971, 0.978, 0.979, 0.981, 0.982, 0.985]

_sw_top5 = [0.355, 0.667, 0.870, 0.973, 0.990, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000]
dtw_top5 = [0.335, 0.564, 0.743, 0.888, 0.942, 0.974, 0.997, 0.999, 1.000, 1.000, 1.000, 1.000, 1.000]
fp1_top5 = [0.809, 0.958, 0.988, 0.999, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000]
fp2_top5 = [0.208, 0.768, 0.915, 0.973, 0.991, 0.998, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000]
fp3_top5 = [0.529, 0.844, 0.950, 0.988, 0.997, 0.999, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000]

strp = "{}&{:s}&{:.3f}&{:.3f}&{:.3f}\\\\{:s}"

# Create latex output for table
for idx, qlen in enumerate(x):
    print("\\hline")
    print(strp.format("", "SW", sw_ranks[idx], _sw_top[idx], _sw_top5[idx], "*"))
    print(strp.format("", "DTW", dtw_ranks[idx], dtw_top[idx], dtw_top5[idx], "*"))
    print(strp.format(qlen, "FP Hash 1", fp1_ranks[idx], fp1_top[idx], fp1_top5[idx], "*"))
    print(strp.format("", "FP Hash 2", fp2_ranks[idx], fp2_top[idx], fp2_top5[idx], "*"))
    print(strp.format("", "FP Hash 3", fp3_ranks[idx], fp3_top[idx], fp3_top5[idx], ""))

fig, (ax1, ax2) = plt.subplots(1, 2)

ax1.plot(x, sw_ranks)
ax1.plot(x, dtw_ranks)
ax1.plot(x, fp1_ranks)
ax1.plot(x, fp2_ranks)
ax1.plot(x, fp3_ranks)
ax1.grid(True)

ax1.set_xticks(range(1, 30))
ax1.set_yticks(np.array(range(1, 11)) / 10)
ax1.set_xlim((5, 15))
ax1.legend(['Smith-Waterman', 'DTW', 'Fingerprint Hash 1', 'Fingerprint Hash 2', 'Fingerprint Hash 3'],
           loc='lower right')
ax1.set_xlabel("Query length")
ax1.set_ylabel("MRR")

ax2.plot(x, _sw_top)
ax2.plot(x, dtw_top)
ax2.plot(x, fp1_top)
ax2.plot(x, fp2_top)
ax2.plot(x, fp3_top)
ax2.grid(True)

ax2.set_xticks(range(1, 30))
ax2.set_yticks(np.array(range(1, 11)) / 10)
ax2.set_xlim((5, 15))
ax2.legend(['Smith-Waterman', 'DTW', 'Fingerprint Hash 1', 'Fingerprint Hash 2', 'Fingerprint Hash 3'],
           loc='lower right')
ax2.set_xlabel("Query length")
ax2.set_ylabel("Accuracy")

plt.show()


##################################
## Hash collision plots

ml = MidiLibrary("nottingham-dataset-master/MIDI/melody")
fp = FingerPrinting(ml, **FingerPrinting.PARAM_SETTING_3)
lens = fp.get_hash_value_lengths()
lens.sort()

_, (ax1, ax2) = plt.subplots(1, 2)

ax1.plot(np.arange(0, 100, 100/len(lens)), lens)
ax1.axvline(x=99, color="r")
ax1.set_xlabel("Different hash values in %")
ax1.set_ylabel("Number Hash Collisions")

ax1.set_xticks(range(0, 101, 10))
# ax1.set_yticks(np.array(range(1, 11))/10)
# ax1.set_xlim((5, 15))
keylist = []
for key in fp._fingerprints:
    if len(fp._fingerprints[key]) > 1000:
        keylist.append((key, len(fp._fingerprints[key])))

keylist.sort(key=lambda x: x[1], reverse=True)

for k in keylist:
    print(k[1], hex(k[0]), k[0]>>24, (k[0]>>16)&0xFF, (k[0]>>8)&0xFF, (k[0]&0xFF))

hashes = list()

for repeat in lens:
    for val in range(int(repeat)):
        hashes.append(repeat)

ax2.hist(hashes, list(range(1, int(lens.max()), 250)))
ax2.axvline(x=fp.quantile, color="r")
ax2.set_xticks(range(0, int(lens.max()), 250))
for tick in ax2.get_xticklabels():
    tick.set_rotation(45)
for tick in ax2.get_yticklabels():
    tick.set_rotation(45)

ax2.set_xlim((1, lens.max()))
ax2.set_xlabel("Hash-collisions")
ax2.set_ylabel("Number of Fingerprints")

plt.show()


##################################
## TIME PERFORMANCE
x = np.array([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])

time = np.array([[0.60498507, 1.24192334, 1.87490765, 2.53736225, 3.26949248, 3.60166865,
                  4.56644251, 4.97236429, 5.72455415, 6.30298477],
                 [0.02189325, 0.0442434, 0.06663363, 0.08940461, 0.11355231, 0.13027534,
                  0.1593588, 0.17672109, 0.20162829, 0.22280612],
                 [0.04237771, 0.06261769, 0.08110421, 0.10263073, 0.11646406, 0.12985652,
                  0.16140884, 0.17382737, 0.20844576, 0.2229424],
                 [0.23704025, 0.46756161, 0.64166553, 0.86028539, 1.17239392, 1.17416942,
                  1.6081467, 1.62091191, 1.95988351, 2.18556531],
                 [0.00882143, 0.01566494, 0.02140228, 0.02699132, 0.03311141, 0.03721151,
                  0.04512914, 0.04696477, 0.05422712, 0.05723306]])

fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [2, 1]})

legend = ["Smith Waterman", "DTW", "Fingerprint Hash 1", "Fingerprint Hash 2", "Fingerprint Hash 3"]
for data in time:
    ax1.plot(x, data)
ax1.legend(legend)
ax1.set_xticks(x)
ax1.grid(True)
ax1.set_xlabel("Database Size")
ax1.set_ylabel("Time per query [s]")

legend2 = ["DTW", "Fingerprint Hash 1", "Fingerprint Hash 3"]

ax2.plot(x, time[1], color="C1")
ax2.plot(x, time[2], color="C2")
ax2.plot(x, time[4], color="C4")
ax2.legend(legend2)
ax2.set_xticks(x)
ax2.grid(True)
ax2.set_xlabel("Database Size")
ax2.set_ylabel("Time per query [s]")

plt.show()

t_norm = time / x
# t_norm = (t_norm.T / t_norm.max(1)).T
t_norm = (t_norm.T / t_norm[:, 0]).T
fig, ax1 = plt.subplots(1, 1)

legend = ["Smith Waterman", "DTW", "Fingerprint Hash 1", "Fingerprint Hash 2", "Fingerprint Hash 3"]
for data in t_norm:
    ax1.plot(x, data)
ax1.legend(legend)
ax1.set_xticks(x)
ax1.grid(True)
ax1.set_xlabel("Database Size")
ax1.set_ylabel("Runtime increase factor per DB item")

plt.show()
