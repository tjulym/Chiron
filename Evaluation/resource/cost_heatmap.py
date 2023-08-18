import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.font_manager
# matplotlib.rcParams["font.family"] = 'Helvetica'
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

# all_costs = [[331.6, 11.8, 8.6, 1, 10.4, 4.2, 3.9, 1.4], [358.2, 9.4, 7.0, 1, 9.4, 4.9, 2.9, 1.5], [61.3, 3.0, 3.0, 1, 3.5, 2.7, 1.6, 0.8], [33.0, 2.0, 1.8, 1, 2.5, 1.5, 1.3, 1.0], [80.0, 6.6, 6.0, 1, 7.4, 1.5, 4.8, 0.9], [59.0, 12.4, 11.7, 1, 16.2, 1.3, 5.9, 1.1], [85.2, 22.4, 21.6, 1, 23.6, 1.7, 10.4, 2.1], [54.8, 20.5, 20.3, 1, 21.0, 1.3, 8.3, 1.1]]

methods = ["OpenFaaS", "SAND", "Faastlane", "Chiron", "Faastlane-M", "Chiron-M", "Faastlane-P", "Chiron-P"]

workflows = ["SN", "MR", "SLApp", "SLApp-V", "FINRA-5", "FINRA-50", "FINRA-100", "FINRA-200"]

all_costs = [
[251.58201904296874, 9.13184814453125, 6.7149951171875, 0.95863671875, 8.08214111328125, 3.3988652343750005, 3.144580078125, 1.2961259765625002], 
[226.39201806640625, 6.169200195312501, 4.655881835937501, 0.8320507812500001, 6.1698935546875004, 3.3141425781250007, 2.0511689453125004, 1.1271689453125002], 
[177.94955810546878, 8.945140625000002, 8.94336328125, 3.1027167968750002, 10.289667968750003, 8.08507080078125, 4.742328125, 2.5585625000000003], 
[253.66569433593753, 15.43526611328125, 13.85888671875, 7.894041992187501, 19.546953125, 12.008392578125001, 10.0807861328125, 8.02267138671875], 
[152.049802734375, 12.71156005859375, 11.660168457031249, 2.1016455078125, 14.190327148437502, 3.0141059570312505, 9.247216796875001, 2.0013940429687502], 
[1295.3115297851562, 272.1898364257812, 257.48768310546876, 22.1482138671875, 355.15611328125004, 28.840587890625002, 129.4514990234375, 24.077240722656253], 
[2565.6019985351563, 673.5569091796875, 651.9146875, 30.309321289062503, 710.7234008789063, 53.48397607421875, 313.95586425781255, 63.034861328125004], 
[5106.182936035157, 1913.101633300781, 1889.9792407226564, 93.37582861328126, 1957.1937231445315, 119.4207109375, 773.1209155273438, 104.9374453125]]

costs_text = []
for i in range(len(methods)):
    costs_text.append([""] * len(workflows))
# print(costs_text)

for i in range(len(workflows)):
    chiron_cost = all_costs[i][3]
    for j in range(len(methods)):
        if j == 3:
            all_costs[i][j] = 1
            costs_text[j][i] = "$%.1f" % chiron_cost
        else:
            all_costs[i][j] = round(all_costs[i][j]/chiron_cost, 1)
            costs_text[j][i] = str(all_costs[i][j])

df_list = []
for i, workflow in enumerate(workflows):
    for j, method in enumerate(methods):
        df_list.append([workflow, method, all_costs[i][j]])

cols = ["workflow", "method", "price"]

df = pd.DataFrame(data=df_list, columns=cols)

print(df)

target = df.pivot(index="method", columns="workflow", values="price")

target.index = pd.CategoricalIndex(target.index, methods)
target.sort_index(level=0, inplace=True)

target.columns = pd.CategoricalIndex(target.columns, workflows)
target.sort_index(axis=1, level=0, inplace=True)

print(target)

ax = sns.heatmap(target, 
    # annot=True, 
    annot=np.array(costs_text), 
    annot_kws={"fontsize": 13},
    fmt="s", 
    # robust=True, 
    linewidth=0.5,
    # cmap=sns.cm.rocket_r, 
    cmap="Blues", 
    cbar_kws={"ticks": [5, 10, 15, 20]},
    vmin=1, vmax=20
    )

plt.subplots_adjust(hspace=None, wspace=None, top=0.99, bottom=0.16, left=0.21, right=1.05)

fontsize = 15
plt.xticks(rotation=30, fontweight="bold", fontsize=fontsize)
plt.yticks(fontweight="bold", fontsize=fontsize)
ax.set_xlabel("")
ax.set_ylabel("")

# ax.vlines(range(1, len(workflows)), *ax.get_ylim())

# plt.savefig('cost_heatmap.pdf')

plt.show()