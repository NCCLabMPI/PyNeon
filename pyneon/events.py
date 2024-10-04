from .data import NeonTabular
import pandas as pd


class NeonEV(NeonTabular):
    """
    Base for Neon event data (blinks, fixations, saccades, "events" messages).
    """

    def __init__(self, file):
        super().__init__(file)

    def __getitem__(self, index) -> pd.Series:
        """Get an event timeseries by index."""
        return self.data.iloc[index]


class NeonBlinks(NeonEV):
    """Blink data."""

    def __init__(self, file):
        super().__init__(file)
        self.data = self.data.astype(
            {
                "blink id": "Int32",
                "start timestamp [ns]": "Int64",
                "end timestamp [ns]": "Int64",
                "duration [ms]": "Int64",
            }
        )


class NeonFixations(NeonEV):
    """Fixation data."""

    def __init__(self, file):
        super().__init__(file)
        self.data = self.data.astype(
            {
                "fixation id": "Int32",
                "start timestamp [ns]": "Int64",
                "end timestamp [ns]": "Int64",
                "duration [ms]": "Int64",
                "fixation x [px]": float,
                "fixation y [px]": float,
                "azimuth [deg]": float,
                "elevation [deg]": float,
            }
        )


class NeonSaccades(NeonEV):
    """Saccade data."""

    def __init__(self, file):
        super().__init__(file)
        self.data = self.data.astype(
            {
                "saccade id": "Int32",
                "end timestamp [ns]": "Int64",
                "duration [ms]": "Int64",
                "amplitude [px]": float,
                "amplitude [deg]": float,
                "mean velocity [px/s]": float,
                "peak velocity [px/s]": float,
            }
        )


class NeonEvents(NeonEV):
    """Event data."""

    def __init__(self, file):
        super().__init__(file)
        self.data = self.data.astype(
            {
                "timestamp [ns]": "Int64",
                "name": str,
                "type": str,
            }
        )
