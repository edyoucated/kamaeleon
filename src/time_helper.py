import pandas as pd
from datetime import datetime
from typing import List


def get_mondays_between(start, end):
    return pd.date_range(start=start, end=end, freq='W-MON').strftime('%Y-%m-%d').tolist()

def get_sundays_between(start, end):
    return pd.date_range(start=start, end=end, freq='W-SUN').strftime('%Y-%m-%d').tolist()

def get_day_delta(start_date: str, end_date: str, include_end_date: bool=True) -> int:
    d0 = datetime.strptime(start_date, "%Y-%m-%d")
    d1 = datetime.strptime(end_date, "%Y-%m-%d")
    delta = d1 - d0
    delta_days = delta.days
    
    if include_end_date:
        delta_days += 1

    return delta_days

def get_time_intervals(starts: List[str], ends: List[str]) -> List[str]:
    return [get_day_delta(start, end, include_end_date=True) for start, end in zip(starts, ends) ]
