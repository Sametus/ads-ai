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

"""
RESET | Target Pos: (1.30, 50.00, -4.88) - escaped

RESET | Target Pos: (-3.99, 50.00, 0.25) - success

RESET | Target Pos: (-2.50, 50.00, 5.60) - escaped

RESET | Target Pos: (2.50, 50.00, 5.45) - high_altitude

RESET | Target Pos: (1.69, 50.00, -2.91) | Rot: (180.00, 147.83)
[EP 5    ] escaped

[EP 6    ] RESET | Target Pos: (6.21, 50.00, 5.05) | Rot: (180.00, 49.89)
[EP 6    ] escaped

[EP 7    ] RESET | Target Pos: (-0.78, 50.00, 8.69) | Rot: (180.00, -1.15)
[EP 7    ] high_altitude

[EP 8    ] RESET | Target Pos: (-4.92, 50.00, -5.52) | Rot: (180.00, 223.67)
[EP 8    ] success

[EP 9    ] RESET | Target Pos: (-1.95, 50.00, 4.73) | Rot: (180.00, -23.47)
[EP 9    ] escaped

[EP 10   ] RESET | Target Pos: (-5.76, 50.00, 3.98) | Rot: (180.00, -55.36)
[EP 10   ] escaped

[EP 11   ] RESET | Target Pos: (-1.97, 50.00, 6.78) | Rot: (180.00, -13.20)
[EP 11   ] escaped      | Ret:   -51.29 | Len:  242 | Start D/H:   49.1 /    0.4 | End D/H:   69.0 /   89.2 | Aln: -0.05 | Succ: 2/11 ( 18.18%) | 23:41:25

[EP 12   ] RESET | Target Pos: (2.63, 50.00, -3.40) | Rot: (180.00, 146.31)
[EP 12   ] escaped      | Ret:   -48.83 | Len:  245 | Start D/H:   48.8 /    0.4 | End D/H:   68.6 /   89.9 | Aln: -0.26 | Succ: 2/12 ( 16.67%) | 23:41:30
[
EP 13   ] RESET | Target Pos: (1.63, 50.00, -5.87) | Rot: (180.00, 167.49)
[EP 13   ] success      | Ret:   231.62 | Len:  138 | Start D/H:   49.0 /    0.4 | End D/H:   11.9 /   40.3 | Aln:  0.14 | Succ: 3/13 ( 23.08%) | 23:41:32

[EP 14   ] RESET | Target Pos: (-3.70, 50.00, 6.38) | Rot: (180.00, -27.11)
[EP 14   ] escaped      | Ret:   -54.98 | Len:  233 | Start D/H:   49.1 /    0.4 | End D/H:   69.4 /   77.7 | Aln: -0.22 | Succ: 3/14 ( 21.43%) | 23:41:36

[EP 15   ] RESET | Target Pos: (-4.06, 50.00, -1.75) | Rot: (180.00, 243.64)
[EP 15   ] success      | Ret:   232.28 | Len:  135 | Start D/H:   48.7 /    0.4 | End D/H:   11.7 /   39.7 | Aln:  0.25 | Succ: 4/15 ( 26.67%) | 23:41:38

[EP 16   ] RESET | Target Pos: (0.79, 50.00, -7.93) | Rot: (180.00, 177.28)
[EP 16   ] success      | Ret:   232.02 | Len:  138 | Start D/H:   49.2 /    0.4 | End D/H:   11.8 /   41.3 | Aln:  0.37 | Succ: 5/16 ( 31.25%) | 23:41:40

[EP 17   ] RESET | Target Pos: (-5.88, 50.00, -3.39) | Rot: (180.00, 235.01)
[EP 17   ] success      | Ret:   233.17 | Len:  131 | Start D/H:   49.0 /    0.4 | End D/H:   11.8 /   37.8 | Aln:  0.62 | Succ: 6/17 ( 35.29%) | 23:41:43

[EP 18   ] RESET | Target Pos: (4.64, 50.00, 5.07) | Rot: (180.00, 43.50)
[EP 18   ] escaped      | Ret:   -53.77 | Len:  235 | Start D/H:   49.1 /    0.4 | End D/H:   69.1 /   62.8 | Aln: -0.05 | Succ: 6/18 ( 33.33%) | 23:41:47

[EP 19   ] RESET | Target Pos: (1.32, 50.00, -2.83) | Rot: (180.00, 151.92)
[EP 19   ] escaped      | Ret:   -49.76 | Len:  239 | Start D/H:   48.7 /    0.4 | End D/H:   68.3 /   69.3 | Aln: -0.04 | Succ: 6/19 ( 31.58%) | 23:41:51

[EP 20   ] RESET | Target Pos: (1.70, 50.00, -7.82) | Rot: (180.00, 167.73)
[EP 20   ] success      | Ret:   234.80 | Len:  132 | Start D/H:   49.2 /    0.4 | End D/H:   11.8 /   38.6 | Aln:  0.99 | Succ: 7/20 ( 35.00%) | 23:41:53

[EP 21   ] RESET | Target Pos: (-0.43, 50.00, 5.99) | Rot: (180.00, -7.10)
[EP 21   ] escaped      | Ret:   -53.41 | Len:  240 | Start D/H:   48.9 /    0.4 | End D/H:   68.9 /   83.8 | Aln: -0.17 | Succ: 7/21 ( 33.33%) | 23:41:56

[EP 22   ] RESET | Target Pos: (-4.91, 50.00, 1.75) | Rot: (180.00, -69.42)
[EP 22   ] escaped      | Ret:   -52.31 | Len:  239 | Start D/H:   48.8 /    0.4 | End D/H:   68.4 /   90.4 | Aln: -0.40 | Succ: 7/22 ( 31.82%) | 23:42:00

[EP 23   ] RESET | Target Pos: (-2.57, 50.00, -5.37) | Rot: (180.00, 202.54)
[EP 23   ] escaped      | Ret:   -48.29 | Len:  238 | Start D/H:   48.9 /    0.4 | End D/H:   68.7 /   79.0 | Aln: -0.18 | Succ: 7/23 ( 30.43%) | 23:42:04

[EP 24   ] RESET | Target Pos: (3.27, 50.00, -2.30) | Rot: (180.00, 129.10)
[EP 24   ] success      | Ret:   231.48 | Len:  138 | Start D/H:   48.8 /    0.4 | End D/H:   11.9 /   42.3 | Aln:  0.16 | Succ: 8/24 ( 33.33%) | 23:42:07

[EP 25   ] RESET | Target Pos: (-0.17, 50.00, -6.00) | Rot: (180.00, 182.64)
[EP 25   ] success      | Ret:   232.30 | Len:  136 | Start D/H:   48.9 /    0.4 | End D/H:   11.8 /   39.5 | Aln:  0.28 | Succ: 9/25 ( 36.00%) | 23:42:09

[EP 26   ] RESET | Target Pos: (-7.49, 50.00, 2.82) | Rot: (180.00, -71.34)
[EP 26   ] success      | Ret:   231.63 | Len:  138 | Start D/H:   49.1 /    0.4 | End D/H:   11.7 /   42.5 | Aln:  0.25 | Succ: 10/26 ( 38.46%) | 23:42:11

[EP 27   ] RESET | Target Pos: (-2.90, 50.00, 2.29) | Rot: (180.00, -52.71)
[EP 27   ] escaped      | Ret:   -51.04 | Len:  238 | Start D/H:   48.7 /    0.4 | End D/H:   68.7 /   83.3 | Aln: -0.08 | Succ: 10/27 ( 37.04%) | 23:42:16

[EP 28   ] RESET | Target Pos: (2.98, 50.00, 0.87) | Rot: (180.00, 74.81)
[EP 28   ] escaped      | Ret:   -47.64 | Len:  244 | Start D/H:   48.7 /    0.4 | End D/H:   68.2 /   86.8 | Aln:  0.18 | Succ: 10/28 ( 35.71%) | 23:42:24

[EP 29   ] RESET | Target Pos: (2.72, 50.00, -8.29) | Rot: (180.00, 159.81)
[EP 29   ] success      | Ret:   231.91 | Len:  136 | Start D/H:   49.4 /    0.4 | End D/H:   11.8 /   39.2 | Aln:  0.21 | Succ: 11/29 ( 37.93%) | 23:42:28

[EP 30   ] RESET | Target Pos: (6.28, 50.00, -3.97) | Rot: (180.00, 123.32)
[EP 30   ] escaped      | Ret:   -51.21 | Len:  240 | Start D/H:   49.2 /    0.4 | End D/H:   69.6 /   66.2 | Aln: -0.19 | Succ: 11/30 ( 36.67%) | 23:42:36

[EP 31   ] RESET | Target Pos: (5.05, 50.00, 2.16) | Rot: (180.00, 62.82)
[EP 31   ] success      | Ret:   231.81 | Len:  135 | Start D/H:   48.9 /    0.4 | End D/H:   11.9 /   40.8 | Aln:  0.28 | Succ: 12/31 ( 38.71%) | 23:42:38

[EP 32   ] RESET | Target Pos: (-2.46, 50.00, 6.09) | Rot: (180.00, -18.99)
[EP 32   ] escaped      | Ret:   -55.87 | Len:  226 | Start D/H:   49.0 /    0.4 | End D/H:   69.3 /   67.2 | Aln: -0.45 | Succ: 12/32 ( 37.50%) | 23:42:43

[EP 33   ] RESET | Target Pos: (-5.88, 50.00, -1.00) | Rot: (180.00, 262.36)
[EP 33   ] success      | Ret:   232.04 | Len:  135 | Start D/H:   48.9 /    0.4 | End D/H:   11.8 /   40.0 | Aln:  0.29 | Succ: 13/33 ( 39.39%) | 23:42:47

[EP 34   ] RESET | Target Pos: (-4.67, 50.00, -5.96) | Rot: (180.00, 221.08)
[EP 34   ] success      | Ret:   233.48 | Len:  131 | Start D/H:   49.1 /    0.4 | End D/H:   12.0 /   37.9 | Aln:  0.77 | Succ: 14/34 ( 41.18%) | 23:42:49

[EP 35   ] RESET | Target Pos: (-7.28, 50.00, 3.73) | Rot: (180.00, -60.85)
[EP 35   ] escaped      | Ret:   -54.41 | Len:  235 | Start D/H:   49.2 /    0.4 | End D/H:   69.4 /   69.7 | Aln: -0.13 | Succ: 14/35 ( 40.00%) | 23:42:54

[EP 36   ] RESET | Target Pos: (-7.91, 50.00, 0.74) | Rot: (180.00, -86.68)
[EP 36   ] escaped      | Ret:   -50.28 | Len:  245 | Start D/H:   49.1 /    0.4 | End D/H:   69.3 /   83.4 | Aln:  0.14 | Succ: 14/36 ( 38.89%) | 23:42:59

[EP 37   ] RESET | Target Pos: (-7.43, 50.00, -1.85) | Rot: (180.00, 258.02)
[EP 37   ] success      | Ret:   233.49 | Len:  132 | Start D/H:   49.1 /    0.4 | End D/H:   11.7 /   39.1 | Aln:  0.79 | Succ: 15/37 ( 40.54%) | 23:43:04

[EP 38   ] RESET | Target Pos: (3.76, 50.00, -2.38) | Rot: (180.00, 118.28)
[EP 38   ] success      | Ret:   233.16 | Len:  132 | Start D/H:   48.8 /    0.4 | End D/H:   11.8 /   38.7 | Aln:  0.63 | Succ: 16/38 ( 42.11%) | 23:43:06

[EP 39   ] RESET | Target Pos: (5.20, 50.00, -1.99) | Rot: (180.00, 113.98)
[EP 39   ] success      | Ret:   231.62 | Len:  136 | Start D/H:   48.9 /    0.4 | End D/H:   12.0 /   40.6 | Aln:  0.27 | Succ: 17/39 ( 43.59%) | 23:43:08

[EP 40   ] RESET | Target Pos: (7.65, 50.00, -2.64) | Rot: (180.00, 105.08)
[EP 40   ] success      | Ret:   231.14 | Len:  139 | Start D/H:   49.3 /    0.4 | End D/H:   11.9 /   41.9 | Aln:  0.09 | Succ: 18/40 ( 45.00%) | 23:43:11

[EP 41   ] RESET | Target Pos: (-2.74, 50.00, 1.62) | Rot: (180.00, -55.40)
[EP 41   ] success      | Ret:   231.31 | Len:  139 | Start D/H:   48.6 /    0.4 | End D/H:   11.9 /   42.6 | Aln: -0.06 | Succ: 19/41 ( 46.34%) | 23:43:14

[EP 42   ] RESET | Target Pos: (-5.97, 50.00, 4.66) | Rot: (180.00, -54.04)
[EP 42   ] escaped      | Ret:   -53.97 | Len:  240 | Start D/H:   49.1 /    0.4 | End D/H:   68.8 /   84.8 | Aln: -0.16 | Succ: 19/42 ( 45.24%) | 23:43:18

[EP 43   ] RESET | Target Pos: (-2.02, 50.00, -3.45) | Rot: (180.00, 207.41)
[EP 43   ] success      | Ret:   233.46 | Len:  131 | Start D/H:   48.7 /    0.4 | End D/H:   11.8 /   38.0 | Aln:  0.66 | Succ: 20/43 ( 46.51%) | 23:43:21

[EP 44   ] RESET | Target Pos: (1.71, 50.00, 3.28) | Rot: (180.00, 23.56)
[EP 44   ] escaped      | Ret:   -49.42 | Len:  248 | Start D/H:   48.7 /    0.4 | End D/H:   68.4 /   90.6 | Aln:  0.29 | Succ: 20/44 ( 45.45%) | 23:43:27

[EP 45   ] RESET | Target Pos: (-5.22, 50.00, -7.33) | Rot: (180.00, 212.46)
[EP 45   ] success      | Ret:   234.12 | Len:  133 | Start D/H:   49.3 /    0.4 | End D/H:   11.8 /   38.5 | Aln:  0.90 | Succ: 21/45 ( 46.67%) | 23:43:29

[EP 46   ] RESET | Target Pos: (-0.76, 50.00, -5.80) | Rot: (180.00, 189.45)
[EP 46   ] success      | Ret:   232.88 | Len:  132 | Start D/H:   48.9 /    0.4 | End D/H:   11.8 /   38.2 | Aln:  0.55 | Succ: 22/46 ( 47.83%) | 23:43:32

[EP 47   ] RESET | Target Pos: (-4.96, 50.00, 0.62) | Rot: (180.00, -87.93)
[EP 47   ] success      | Ret:   234.53 | Len:  130 | Start D/H:   48.8 /    0.4 | End D/H:   11.8 /   37.7 | Aln:  0.88 | Succ: 23/47 ( 48.94%) | 23:43:34

[EP 48   ] RESET | Target Pos: (4.90, 50.00, -7.55) | Rot: (180.00, 148.01)
[EP 48   ] escaped      | Ret:   -49.25 | Len:  241 | Start D/H:   49.4 /    0.4 | End D/H:   69.2 /   79.5 | Aln:  0.02 | Succ: 23/48 ( 47.92%) | 23:43:38

[EP 49   ] RESET | Target Pos: (-6.62, 50.00, -0.97) | Rot: (180.00, 263.67)
[EP 49   ] success      | Ret:   231.67 | Len:  137 | Start D/H:   49.0 /    0.4 | End D/H:   11.8 /   41.5 | Aln:  0.25 | Succ: 24/49 ( 48.98%) | 23:43:41

RESET | Target Pos: (-4.75, 50.00, 6.61) - escaped

RESET | Target Pos: (5.66, 50.00, -2.65) - success

RESET | Target Pos: (2.90, 50.00, -3.50) - escaped

RESET | Target Pos: (7.97, 50.00, -0.24) - escaped

RESET | Target Pos: (5.82, 50.00, 2.21) - escaped

RESET | Target Pos: (4.39, 50.00, 5.46) - escaped

RESET | Target Pos: (4.61, 50.00, -3.10) - escaped

RESET | Target Pos: (-0.93, 50.00, 3.95) - escaped

RESET | Target Pos: (3.77, 50.00, 2.72) - escaped

RESET | Target Pos: (4.18, 50.00, 3.28) - escaped

RESET | Target Pos: (-6.84, 50.00, -1.08) - success
"""