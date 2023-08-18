import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
# import pandas as pd
# import seaborn as sns
import matplotlib.font_manager
# matplotlib.rcParams["font.family"] = 'Helvetica'
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

methods = ["OpenFaaS", "SAND", "Faastlane", "Chiron", "Faastlane-M", "Chiron-M", "Faastlane-P", "Chiron-P"]

workflows = ["SocialNetwork", "MovieReviewing", "SLApp", "SLApp-V", "FINRA-5", "FINRA-50", "FINRA-100", "FINRA-200"]

all_mems = [[337, 33, 33, 30, 39, 37, 67, 65], [301, 30, 30, 28, 34, 34, 59, 59], [165, 36, 29, 28, 33, 33, 48, 48], [165, 29, 28, 27, 60, 60, 47, 47], [182, 57, 57, 53, 78, 65, 82, 79], [1595, 63, 63, 57, 68, 324, 338, 335], [3165, 146, 146, 114, 149, 477, 660, 614], [6305, 205, 205, 172, 211, 792, 1259, 1148]]

for i, workflow_mems in enumerate(all_mems):
    print(f"==={workflows[i]}===")
    for j, method in enumerate(methods):
        print(f"{method}: {workflow_mems[j]} MB")

chiron_mems = []
for i in range(len(all_mems)):
    chiron_mem = all_mems[i][3]
    chiron_mems.append(chiron_mem)

    for j in range(len(all_mems[i])):
        all_mems[i][j] = all_mems[i][j] * 1.0 / chiron_mem

nor_th_text = []

all_ths = [[1344.0, 2080.0, 2592.0, 33200, 2032.0, 4120.0, 6000.0, 16800.0], [1457.7777777777778, 2560.0, 3160.0, 35840, 2500.0, 5200.0, 8480.0, 17600.0], [1120.0, 1900.0, 1900.0, 5200.0, 1560.0, 2133.3333333333335, 3260.0, 6800.0], [384.0, 1152.0, 1280.0, 2106.6666666666665, 704.0, 1120.0, 1680.0, 2100.0], [1480.0, 1168.0, 1232.0, 13600, 1040.0, 6160, 1824.0, 13040], [58.03921568627451, 59.2, 60.8, 1026.6666666666667, 52.8, 520.0, 132.8, 690.9090909090909], [16.633663366336634, 22.4, 23.2, 506.6666666666667, 19.2, 257.77777777777777, 54.4, 289.5238095238095], [4.776119402985074, 9.6, 10.0, 189.0909090909091, 8.4, 131.42857142857142, 21.2, 144.76190476190476]]

# print(all_ths)

for i in range(len(workflows)):
    chiron_th = all_ths[i][3]

    nor_th_text.append(int(chiron_th/10))

    for j in range(len(methods)):
        all_ths[i][j] = all_ths[i][j] * 1.0 / chiron_th


fig, axes = plt.subplots(2, 1, sharex=True, facecolor='w', gridspec_kw={'height_ratios': (1, 1)}, figsize=(9.3, 3), dpi=300)

plt.subplots_adjust(hspace=0.05, wspace=None, top=0.91, bottom=0.08, left=0.055, right=0.99)

width = 0.07
gap = 0.02

colors = ["#009E73", "#F0F0F0", "#57B5E8", "k", "#00FFFF", "#D53E4F", "#00BFFF",   "#66C2A5"]
colors = ["#009E73", "#F0F0F0", "#57B5E8", "k", "#00FFFF", "#D53E4F", "#9400D3",   "#66C2A5"]
hatches = ["xxxx",    None,       None,     "///", None,     "///",       None,      "///"]

linewidth = 0.5

mpl.rcParams['hatch.linewidth'] = 0.5

back_colors = ["#9ECAE1", "#6BAED6", "#3182BD", "white", "#08519C", "white", "#800080", "white"]
back_colors = ["#9ECAE1", "#6BAED6", "#3182BD", "#08519C", "white", "white", "white", "white"]

edge_colors = ["#9ECAE1", "#6BAED6", "#3182BD", "k", "#08519C", "k", "#800080", "k"]
edge_colors = ["#9ECAE1", "#6BAED6", "#3182BD", "k", "#08519C", "r", "#800080", "blue"]

edge_colors = ["k", "k", "k", "k", "#3182BD", "#08519C","#3182BD", "#08519C"]

hatches = [None, None, None, "////", None, "\\\\\\\\", None, "xxxx"]
hatches = [None, None, None, "////", None, "////", None, "////"]

hatches = [None, None, None, None, "///", "\\\\\\", "////////", "\\\\\\\\\\\\\\\\"]

bars = []
text_fontdict2 = {"size": 7, "family": "Consolas"}

for i in range(len(workflows)):
    for j in range(len(methods)):
        x = i + (j - 3.5) * (width + gap)

        if hatches[j] is None:
            bar = axes[0].bar([x], [all_mems[i][j]], width=width, color=back_colors[j], edgecolor="#000000", linewidth=linewidth, zorder=2)
            axes[1].bar([x], [all_ths[i][j]], width=width, color=back_colors[j], edgecolor="#000000", linewidth=linewidth, zorder=2)
            if i == 0:
                bars.append(bar)
        else:
            # bar1 = axes[0].bar([x], [all_mems[i][j]], width=width, color=back_colors[j], edgecolor=edge_colors[j], hatch=hatches[j], linewidth=linewidth, zorder=2)
            bar1 = axes[0].bar([x], [all_mems[i][j]], width=width, color=back_colors[j], edgecolor="k", hatch=hatches[j], linewidth=linewidth, zorder=2)
            bar2 = axes[0].bar([x], [all_mems[i][j]], width=width, color="none", edgecolor="k", linewidth=linewidth, zorder=2)

            axes[1].bar([x], [all_ths[i][j]], width=width, color=back_colors[j], edgecolor="k", hatch=hatches[j], linewidth=linewidth, zorder=2)
            axes[1].bar([x], [all_ths[i][j]], width=width, color="none", edgecolor="k", linewidth=linewidth, zorder=2)

            if i == 0:
                bars.append((bar1, bar2))

        if all_mems[i][j] > 8:
            xs = np.linspace(x - width/2 - 0.01, x + width/2 + 0.01, 100)
            # print(xs)
            ys1 = []
            ys2 = []
            for xx in xs:
                ys1.append(6.8 + 0.2 * ((xx - (x - width/2 - 0.01))/(width + 0.02)))
                ys2.append(7.0 + 0.2 * ((xx - (x - width/2 - 0.01))/(width + 0.02)))

            axes[0].fill_between(xs, ys1, ys2, color="white", zorder=3)

            axes[0].plot([x - width/2 - 0.01, x + width/2 + 0.01], [6.8, 7.0], color="k", lw=0.5, zorder=4)
            axes[0].plot([x - width/2 - 0.01, x + width/2 + 0.01], [7.0, 7.2], color="k", lw=0.5, zorder=4)

            axes[0].text(x + width/2 + 0.02, 7, str(round(all_mems[i][j], 1)), va="center", fontdict=text_fontdict2)

        if j == 3:
            axes[0].text(x, 1.2, "%dMB" % chiron_mems[i], rotation=90, 
                va="center", rotation_mode='anchor', 
                fontdict=text_fontdict2,
                # color="#FF1E1E"
                )

            axes[1].text(x, 1, "%d" % nor_th_text[i], 
                va="bottom", ha="center", rotation_mode='anchor', 
                fontdict=text_fontdict2,
                # color="#FF1E1E"
                )


axes[0].set_ylabel("Norm. Memory", labelpad=13)
axes[1].set_ylabel("Norm. Throughput")

axes[0].set_xticks([])

axes[0].xaxis.set_tick_params(length=0)


axes[0].set_ylim(0, 8)
axes[0].set_yticks(range(1, 8, 2))


axes[0].grid(ls="--", zorder=1, axis="y")
axes[1].grid(ls="--", zorder=1, axis="y")

axes[0].legend(bars, methods, ncol=8, framealpha=0.5, loc=(0.01, 1), frameon=False, columnspacing=0.9, handletextpad=0.4, fontsize=10)

plt.xlim(0 - 3.5 * (width + gap) - 2 * width, len(workflows) - 1  + 3.5 * (width + gap) + 2 * width)

plt.xticks(range(len(workflows)), workflows)

# plt.savefig('mem-and-ths.pdf')

plt.show()

# print(all_mems)
# print(all_ths)
