
import pandas as pd

def parse_epw(epw_file, month):
    df = pd.read_csv(epw_file, skiprows=8, header=None)
    df.columns = ["year","month","day","hour","minute","dry_bulb","dew_point","rh"] + list(range(df.shape[1]-8))
    m = df[df["month"] == month]
    return m["dry_bulb"].mean(), m["rh"].mean()
