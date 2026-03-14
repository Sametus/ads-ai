import pandas as pd
import numpy as np
import plotly.express as px


eps = pd.read_csv(r"C:\Users\husey\Desktop\ads_ai\logs\episode_log.csv")

ep = list()
sc = list()

for i in range(1, eps.shape[0]):
    sc_ = eps.loc[1:i]
    sc__ = sc_[sc_["done_reason"] == "success"].shape[0]
    scr = sc__ * 100 / sc_.shape[0]
    ep.append(i)
    sc.append(scr)

df = pd.DataFrame({"episode": ep, "score": sc})
fig = px.line(data_frame=df,x="episode",y="score")
fig.show()