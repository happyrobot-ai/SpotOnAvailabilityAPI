import pandas as pd
import numpy as np

df = pd.read_csv(
    "/Users/beltranscg/HappyRobot/CMA-CGM/SpotOn/Qlik Sense Port Pairs SpotOn.csv",
    skiprows=1,
    delimiter=";",
    index_col="POL-POD Booked",
)
# df = df.set_index("Date")

# print(df.index.values[0:5])
print(df.head(n=5))
print(df.loc["BJCOO-BRPEC"])
