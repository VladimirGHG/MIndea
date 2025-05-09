import os, json
import numpy as np
import pandas as ps
from pandas import DataFrame
import matplotlib.pyplot as plt
import seaborn as sns

def show_piechart():
    TASK_FILE = "tasks.json"
    tasks_grouped = {"names": [], "time": []}

    def load_tasks():
        if os.path.exists(TASK_FILE):
            with open(TASK_FILE, "r") as f:
                tasks = json.load(f)
                for name, task_info in tasks.items():
                    if task_info["time"] != 0:
                        tasks_grouped["names"].append(name) 
                        tasks_grouped["time"].append(task_info["time"])


    load_tasks()

    def time_label(value):
        total_seconds = int(value)
        hours, remainder = divmod(total_seconds, 3600)
        minutes = remainder // 60
        return f"{hours}h {minutes}m"


    task_df = DataFrame(tasks_grouped)
    colors = sns.color_palette("magma", len(task_df))
    plt.pie(
        task_df["time"], 
        labels=list(task_df["names"].apply(lambda x: x.capitalize())), 
        startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 4, 'linestyle': 'solid', 'alpha': 0.8},
        autopct=lambda p: time_label(p * sum(task_df["time"]) / 100),
        colors=colors
    )

    plt.show()