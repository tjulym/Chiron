import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.font_manager
# matplotlib.rcParams["font.family"] = 'Helvetica'
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


# methods = ["ASF", "OpenFaaS", "SAND", "Faastlane", "Chiron", "Faastlane-M", "Chiron-M", "Chiron-PC", "Faastlane-P", "Chiron-P"]
# methods = ["OpenFaaS", "SAND", "Faastlane", "Chiron", "Faastlane-M", "Chiron-M", "Faastlane-P", "Chiron-P"]

# methods = ["One-to-One",  "Many-to-One", "Chiron",  "Chiron-M", "Chiron-P"]
methods = ["OpenFaaS",  "Faastlane", "Chiron",  "Chiron-M", "Chiron-P"]

workflows = ["SocialNetwork", "MovieReviewing", "SLApp", "SLApp-V", "FINRA-5", "FINRA-50", "FINRA-100", "FINRA-200"]
workflows = ["SN", "MR", "SLApp", "SLApp-V", "FINRA-5", "FINRA-50", "FINRA-100", "FINRA-200"]

colors = ["#009E73",  "#57B5E8", "k",  "#D53E4F",   "#66C2A5"]
hatches = ["xxxx",      None,    "///",  "///",         "///"]

back_colors = ["#9ECAE1",  "#3182BD", "white",  "white",  "white"]

back_colors = ["#C6DBEF", "#9ECAE1", "#6BAED6", "#3182BD", "#08519C",]
back_colors = ["#C6DBEF", "#6BAED6", "white", "#3182BD", "#08519C",]

edge_colors = ["#9ECAE1",  "#3182BD", "k", "r", "blue"]

hatches = [None, None,  "////",  "////",  "////"]

hatches = [None, None,  None,  None,  None]
hatches = [None, None,  "//////",  None,  None]

# ASF, OpenFaaS, SAND, Faastlane, Chiron, Faastlane-M, Chiron-M, Chiron-PC, Faastlane-P, Chiron-P
SN_lats =        [ 744, 72,  85,  62,  36,  75,  76,  66,   28, 26]
SN_CPUs =        [ 10,  10,  5,   5,   1,   5,   2,   2,    5,  2]

# print(1+10+9+1+2+1+1+13+20+17)
# exit(0)

SN_CPU_costs =   [ 75,  75, 425, 310,  36, 375, 152, 132, 140, 52]

# print(39.2 + 36.04 + 29.61 + 39.25 + 28.3 + 27.83 + 35.77 + 27.59 + 37.67)
# exit(0)

MR_lats =        [ 707, 65,  71,  53,  30,  71,  74,  54,   22, 22]
MR_CPUs =        [ 9,   9,   4,   4,   1,   4,   2,   2,    4,  2]

# print(1+9+9+1+1+1+13+15+16)
# exit(0)
MR_CPU_costs =   [ 66,  66, 284, 212,  30, 284, 148, 108,   88, 44]


App7_lats =      [443,  83,  104, 104, 69,  120, 125, 115,  54, 56]
App7_CPUs =      [ 7,   7,   4,   4,   2,   4,   3,   2,    4,  2]

App7_CPU_costs = [140, 140, 416, 416, 138, 480, 375, 230, 216, 112]

# print(18+11+18+30+17+17+16+18+11+18)
# exit(0)

App10_lats =     [ 889, 172, 145, 130, 122, 184, 187, 128,  94, 93]
App10_CPUs =     [ 10,  10,  5,   5,   3,   5,   3,   4,    5,  4]

App10_CPU_costs = [174, 174, 725, 650, 366, 920, 561, 512, 470, 372]


Finra_5_lats =   [ 459, 107, 119, 109,  90, 133, 133, 124,  86, 85]
Finra_5_CPUs =   [ 6,    6,   5,   5,    1,  5,   1,   1,    5,  1]
# print(92+1*5)
# exit(0)

Finra_5_CPU_costs =[97, 97,  595, 545,  90, 665, 133, 124, 430, 85]


Finra_50_lats =  [1711, 305, 259, 245, 174, 338, 228, 244, 123, 103]
Finra_50_CPUs =  [51,   51,  50,  50,   6,  50,  6,   11,  50,  11]

                                                #59+53*5
Finra_50_Mems = [1595, 1595,  63, 63,  57,  68,  324, 335, 338, 335]

# print((92+4) * 10 +1)
# exit(0)
                                                        #228*6-4-8-12-16-20
Finra_50_CPU_costs=[961, 961, 12950, 12250, 1044, 16900, 1308, 2684, 6150, 1133]

Finra_100_lats = [3732, 482, 351, 338, 285, 373, 339, 483, 159, 142]
Finra_100_CPUs = [101,  101, 100, 100, 6,   100,   9,  21, 100, 21]

                            #70+76,        #73+76        #490+170
Finra_100_Mems =[3165, 3165, 146, 146, 114, 149, 477, 614, 660, 614]
                                               #61+52*8

# print((92+4) * 20 +1)
# exit(0)
Finra_100_CPU_costs= [1921, 1921, 351*80+199*20, 338*80+199*20, 1430, 373*80+199*20, 
339+234+239+243+240+281+233+319+318, 483*21, 159*80+110*20, 142*21]

Finra_200_lats = [8530, 838, 496, 482, 414, 522, 483, 891, 231, 236]
Finra_200_CPUs = [201,  201, 200, 200, 11,  200,  14,  21, 200, 21]

                            #70+72+63  57+115   64+56*13    #490+496+273    
Finra_200_Mems =[6305, 6305, 205, 205, 172, 211, 792, 1148, 1259, 1148]
                                          #76+72+63

# print((92+4) * 40 +1)
# exit(0)

Finra_200_CPU_costs= [3841, 3841, 496*80+461*80+363*40, 482*80+461*80+363*40, 414*6+389*5, 
522*80+461*80+363*40, 483+376+376+379+378+376+404+391+407+370+369+427+348+433, 891*21, 231*80+164*80+129*40, 236*21]

# fig, axes = plt.subplots(3, 1, sharex=True, facecolor='w', gridspec_kw={'height_ratios': (1, 1, 3)}, figsize=(9.3, 1.8), dpi=300)

fig  =  plt.figure(figsize=(4.65, 1.8), dpi=300)

plt.subplots_adjust(hspace=None, wspace=None, top=0.98, bottom=0.2, left=0.1, right=0.99)

width = 0.15
gap = 0.02

# all_lats = [SN_lats, MR_lats, App7_lats, App10_lats, Finra_5_lats, Finra_50_lats, Finra_100_lats, Finra_200_lats]

# all_mems = [SN_Mems, MR_Mems, App7_Mems, App10_Mems, Finra_5_Mems, Finra_50_Mems, Finra_100_Mems, Finra_200_Mems]

all_cpu_costs = [SN_CPU_costs, MR_CPU_costs, App7_CPU_costs, App10_CPU_costs, Finra_5_CPU_costs, Finra_50_CPU_costs, Finra_100_CPU_costs, Finra_200_CPU_costs]

all_cpus = [SN_CPUs, MR_CPUs, App7_CPUs, App10_CPUs, Finra_5_CPUs, Finra_50_CPUs, Finra_100_CPUs, Finra_200_CPUs]

for i, workflow_cpus in enumerate(all_cpus):
    print(f"==={workflows[i]}===")
    for j, method in enumerate(["ASF", "OpenFaaS", "SAND", "Faastlane", "Chiron", "Faastlane-M", "Chiron-M", "Chiron-PC", "Faastlane-P", "Chiron-P"]):
        if j != 7:
            print(f"{method}: {workflow_cpus[j]} CPUs")

for i in range(len(workflows)):
    all_cpus[i].pop(-5)
    all_cpus[i].pop(-3)
    all_cpus[i].pop(-2)
    all_cpus[i].pop(2)
    all_cpus[i].pop(0)

    for j in range(len(all_cpus[i])):
        if j != 2:
            if all_cpus[i][j] % all_cpus[i][2] > 0:
                all_cpus[i][j] = round(all_cpus[i][j]/all_cpus[i][2], 2)
            else:
                all_cpus[i][j] = int(all_cpus[i][j]/all_cpus[i][2])

    all_cpus[i][2] = 1

    # print(all_cpus[i])

# exit(0)

linewidth = 0.5

mpl.rcParams['hatch.linewidth'] = 0.5

bars = []
# text_fontdict2 = {"size": 7, "family": "Consolas"}
text_fontdict2 = {"size": 9, "family": "Consolas"}

for i in range(len(workflows)):
    for j in range(len(methods)):
        x = i + (j - 2) * (width + gap)

        if hatches[j] is None:
            bar = plt.bar([x], [all_cpus[i][j]], width=width, color=back_colors[j], edgecolor="#000000", linewidth=linewidth, zorder=2)
            if i == 0:
                bars.append(bar)
        else:
            bar1 = plt.bar([x], [all_cpus[i][j]], width=width, color=back_colors[j], edgecolor=edge_colors[j], hatch=hatches[j], linewidth=linewidth, zorder=2)
            bar2 = plt.bar([x], [all_cpus[i][j]], width=width, color="none", edgecolor="k", linewidth=linewidth, zorder=2)
            if i == 0:
                bars.append((bar1, bar2))

        if all_cpus[i][j] > 10:
                xs = np.linspace(x - width/2 - 0.01, x + width/2 + 0.01, 100)
                # print(xs)
                ys1 = []
                ys2 = []

                if i == 6:
                    y = 9
                else:
                    y = 8

                for xx in xs:
                    ys1.append(y-0.2 + 0.2 * ((xx - (x - width/2 - 0.01))/(width + 0.02)))
                    ys2.append(y + 0.2 * ((xx - (x - width/2 - 0.01))/(width + 0.02)))

                plt.fill_between(xs, ys1, ys2, color="white", zorder=3)

                plt.plot([x - width/2 - 0.01, x + width/2 + 0.01], [y-0.2, y], color="k", lw=0.5, zorder=4)
                plt.plot([x - width/2 - 0.01, x + width/2 + 0.01], [y, y+0.2], color="k", lw=0.5, zorder=4)

                if j == 0:
                    plt.text(x - width/2 - 0.02, y, str(round(all_cpus[i][j], 1)), va="center", fontdict=text_fontdict2, ha="right")
                else:
                    plt.text(x + width/2 + 0.02, y, str(round(all_cpus[i][j], 1)), va="center", fontdict=text_fontdict2)

        # plt.text(x, 25, str(all_cpus[i][j]), rotation=90, ha="right", va="center", rotation_mode='anchor', fontdict=text_fontdict2)


plt.ylabel("Norm. CPU Allocation")

plt.ylim(0, 10)
plt.yticks(range(1, 11, 2))

# plt.yscale("log")

plt.grid(ls="--", zorder=1, axis="y")

# plt.legend(bars, methods, ncol=2, framealpha=0.5, loc=(0, 0.4), frameon=False, columnspacing=0.9, handletextpad=0.4, fontsize=10)
plt.legend(bars, methods, ncol=2, framealpha=0.5, loc=(0.129, 0.55), 
    frameon=True, columnspacing=0.9, handletextpad=0.4, fontsize=10)

plt.xlim(0 - 2 * (width + gap) - 2 * width, len(workflows) - 1  + 2 * (width + gap) + 2 * width)

plt.xticks(range(len(workflows)), workflows, rotation=20)
plt.gca().xaxis.set_tick_params(pad=-2, length=1)

# plt.savefig('cpu-com-model.pdf')

plt.show()

# print(all_cpus)
