"""
Indicator normalisation for Penumbra.

Each raw indicator lives on a different scale: reais, years of schooling,
people per square kilometre. To sum them into a single index they all need to
go onto the same ruler, from 0 to 1, where 1 means deeper in the penumbra.
That is what these functions do.

The default ruler is the percentile rank within the municipality set, which is
robust to extreme values like Salvador. For long-tailed indicators such as
population and income, a log transform is applied first, so the gap between a
tiny town and a medium one counts as much as the gap between a medium and a large one.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

LOWER_IS_WORSE = "lower_is_worse"
HIGHER_IS_WORSE = "higher_is_worse"


def percentile_rank(series: pd.Series, log: bool = False) -> pd.Series:
    """Converts values to their percentile rank within the set, from 0 to 1.

    Missing values stay missing and are handled later. With log enabled, the
    transform only applies to positive values.
    """
    values = series.astype(float)
    if log:
        values = np.log(values.where(values > 0))
    return values.rank(pct=True)


def score(series: pd.Series, direction: str, log: bool = False) -> pd.Series:
    """Returns the penumbra score for one indicator, between 0 and 1.

    When lower values are worse (low income), the score is the inverse of the
    percentile rank. When higher values are worse (distance), it is the rank
    itself.
    """
    p = percentile_rank(series, log=log)
    return (1 - p) if direction == LOWER_IS_WORSE else p


def minmax(series: pd.Series) -> pd.Series:
    """Rescales linearly to the 0-to-1 interval."""
    values = series.astype(float)
    low, high = values.min(), values.max()
    if not np.isfinite(low) or high == low:
        return pd.Series(0.5, index=values.index)
    return (values - low) / (high - low)


def row_mean(frame: pd.DataFrame) -> pd.Series:
    """Row-wise mean ignoring missing values.

    Used to combine sub-indicators when not all of them exist for every
    municipality. If a municipality has none of the sub-indicators, the result
    stays missing and imputation handles it later.
    """
    return frame.mean(axis=1, skipna=True)
