import json

import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.font_manager
matplotlib.rcParams["font.family"] = 'Helvetica'
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

methods = ["Chiron-Predictor", "RFR", "LSTM", "GNN"]
workflows = ["sn", "mr", "finra", "SLApp", "SLApp-V"]

workflow_map = {"sn": "SN", "mr": "MR", "finra": "FINRA-5", "SLApp": "SLApp", "SLApp-V": "SLApp-V"}

chrion_preds = []

def get_data(file_path=""):
    res = []
    for method in methods:
        for workflow in workflows:
            with open("loss%s/%s/loss_%s.csv" % (file_path, method, workflow), "r") as f:
                lines = f.readlines()
            for line in lines:
                res.append([method, workflow_map[workflow], abs(float(line))*100])

    avg_losss = []
    for workflow in workflows:
        print(f"==={workflow}===")
        for method in methods:
            losss = [abs(r[2]) for r in res if r[0] == method and r[1] == workflow_map[workflow]]

            avg_losss.append(sum(losss)/len(losss))
            print(f"{method}: {avg_losss[-1]}")

            if method == 'Chiron-Predictor':
                chrion_preds.append(avg_losss[-1])


    cols = ["method", "workflow", "acc"]

    df = pd.DataFrame(data=res, columns=cols)

    return df, avg_losss

fig, axes = plt.subplots(1, 3, facecolor='w', gridspec_kw={'width_ratios': (1, 1, 1)}, figsize=(9.3, 1.8), dpi=300)

plt.subplots_adjust(hspace=None, wspace=None, top=0.88, bottom=0.2, left=0.06, right=0.99)

# text_fontdict = {"size": 12, "weight": "bold"}
text_fontdict = {"size": 12}

text_fontdict2 = {"size": 7, "family": "Consolas"}

my_pal = {
    "Chiron-Predictor": "#C6DBEF",
    "RFR": "#6BAED6", 
    "LSTM": "#3182BD", 
    "GNN": "#08519C", }

text_y = [380, 140, 380]

ylims = [(-100, 510), (-100, 200), (-100, 510)]

ylims = [(0, 510), (0, 200), (0, 510)]
ylims = [(0, 400), (0, 150), (0, 400)]

titles = ["(a) Native Thread", "(b) Intel MPK", "(c) Process Pool"]

for index, file_path in enumerate(["", "-mpk", "-pp"]):
    print(titles[index])
    df, avg_losss = get_data(file_path)

    ax = sns.boxplot(x="workflow", y="acc", data=df, hue="method", palette=my_pal, linewidth=0.8, ax=axes[index], showfliers=False)

    axes[index].set_ylim(ylims[index][0], ylims[index][1])        

    axes[index].grid(linestyle="--", alpha=0.5)

    axes[index].set_ylabel("")

    axes[index].set_xlabel(titles[index], labelpad=0.5)

axViolin, axLabel = axes[0].get_legend_handles_labels()

fig.legend(axViolin, axLabel, fontsize=text_fontdict["size"], ncol=4, frameon=False, loc=(0.15, 0.85), columnspacing=5)

axes[0].get_legend().remove()
axes[1].get_legend().remove()
axes[2].get_legend().remove()



print(sum(chrion_preds)/len(chrion_preds))

axes[0].set_ylabel("Prediction Error (%)", fontdict=text_fontdict)

# plt.savefig('workflow_eval-all.pdf')
plt.show()