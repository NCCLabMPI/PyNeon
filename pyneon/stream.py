from pathlib import Path
import pandas as pd
import numpy as np
from numbers import Number
from typing import Union, Literal

from .data import NeonTabular
from .preprocess import crop, interpolate


class NeonStream(NeonTabular):
    """
    Base for Neon continuous data (gaze, eye states, IMU).
    It must contain a ``timestamp [ns]`` column.

    Parameters
    ----------
    file : :class:`pathlib.Path`
        Path to the CSV file containing the stream data.

    Attributes
    ----------
    file : :class:`pathlib.Path`
        Path to the CSV file containing the stream data.
    data : pandas.DataFrame
        DataFrame containing the stream data.
    timestamps : np.ndarray
        Timestamps of the stream in nanoseconds.
    ts : np.ndarray
        Alias for timestamps.
    first_ts : int
        First timestamp of the stream.
    last_ts : int
        Last timestamp of the stream.
    times : np.ndarray
        Timestamps converted to seconds relative to stream start.
    duration : float
        Duration of the stream in seconds.
    sampling_freq_effective : float
        Effective sampling frequency of the stream
        (number of time points divided by duration).
    sampling_freq_nominal : int
        Nominal sampling frequency of the stream as specified by Pupil Labs
        (https://pupil-labs.com/products/neon/specs).
    """

    def __init__(self, file: Path):
        super().__init__(file)
        self._get_attributes()

    def _get_attributes(self):
        """
        Get attributes given self.data DataFrame.
        """
        self.timestamps = self.data.index.to_numpy()
        self.ts = self.timestamps
        self.first_ts = int(self.ts[0])
        self.last_ts = int(self.ts[-1])
        self.times = (self.ts - self.first_ts) / 1e9
        self.data["time [s]"] = self.times
        self.duration = float(self.times[-1] - self.times[0])
        self.sampling_freq_effective = self.data.shape[0] / self.duration

    def crop(
        self,
        tmin: Union[Number, None] = None,
        tmax: Union[Number, None] = None,
        by: Literal["timestamp", "time"] = "timestamp",
        inplace: bool = False,
    ) -> pd.DataFrame:
        """
        Crop data to a specific time range.

        Parameters
        ----------
        tmin : number, optional
            Start time or timestamp to crop the data to. If ``None``,
            the minimum timestamp or time in the data is used. Defaults to ``None``.
        tmax : number, optional
            End time or timestamp to crop the data to. If ``None``,
            the maximum timestamp or time in the data is used. Defaults to ``None``.
        by : "timestamp" or "time", optional
            Whether tmin and tmax are UTC timestamps in nanoseconds
            or relative times in seconds. Defaults to "timestamp".
        inplace : bool, optional
            Whether to replace the data in the object with the cropped data.
            Defaults to False.

        Returns
        -------
        pd.DataFrame
            Cropped data.
        """
        new_data = crop(self.data, tmin, tmax, by)
        if inplace:
            self.data = new_data
            self._get_attributes()
        return new_data

    def interpolate(
        self,
        new_ts: Union[None, np.ndarray] = None,
        float_kind: str = "linear",
        other_kind: str = "nearest",
        inplace: bool = False,
    ) -> pd.DataFrame:
        """
        Interpolate the stream to a new set of timestamps.

        Parameters
        ----------
        new_ts : np.ndarray, optional
            New timestamps to evaluate the interpolant at. If ``None``, new timestamps
            are generated according to the nominal sampling frequency of the stream as
            specified by Pupil Labs: https://pupil-labs.com/products/neon/specs.
        data : pd.DataFrame
            Data to interpolate. Must contain a monotonically increasing
            ``timestamp [ns]`` column.
        float_kind : str, optional
            Kind of interpolation applied on columns of float type,
            by default "linear". For details see :class:`scipy.interpolate.interp1d`.
        other_kind : str, optional
            Kind of interpolation applied on columns of other types,
            by default "nearest".

        Returns
        -------
        pandas.DataFrame
            Interpolated data.
        """
        # If new_ts is not provided, generate a evenly spaced array of timestamps
        if new_ts is None:
            step_size = int(1e9 / self.sampling_freq_nominal)
            new_ts = np.arange(self.first_ts, self.last_ts, step_size, dtype=np.int64)
            assert new_ts[0] == self.first_ts
            assert np.all(np.diff(new_ts) == step_size)
        new_data = interpolate(new_ts, self.data, float_kind, other_kind)
        if inplace:
            self.data = new_data
            self._get_attributes()
        return new_data


class NeonGaze(NeonStream):
    """
    Gaze data that inherits attributes and methods from :class:`NeonStream`.
    """

    def __init__(self, file: Path):
        super().__init__(file)
        self.sampling_freq_nominal = int(200)
        self.data = self.data.astype(
            {
                "gaze x [px]": float,
                "gaze y [px]": float,
                "worn": bool,
                "fixation id": "Int32",
                "blink id": "Int32",
                "azimuth [deg]": float,
                "elevation [deg]": float,
                "time [s]": float,
            }
        )


class NeonEyeStates(NeonStream):
    """
    3D eye states data that inherits attributes and methods from :class:`NeonStream`.
    """

    def __init__(self, file: Path):
        super().__init__(file)
        self.sampling_freq_nominal = 200
        self.data = self.data.astype(
            {
                "pupil diameter left [mm]": float,
                "pupil diameter right [mm]": float,
                "eyeball center left x [mm]": float,
                "eyeball center left y [mm]": float,
                "eyeball center left z [mm]": float,
                "eyeball center right x [mm]": float,
                "eyeball center right y [mm]": float,
                "eyeball center right z [mm]": float,
                "optical axis left x": float,
                "optical axis left y": float,
                "optical axis left z": float,
                "optical axis right x": float,
                "optical axis right y": float,
                "optical axis right z": float,
                "time [s]": float,
            }
        )


class NeonIMU(NeonStream):
    """
    IMU data that inherits attributes and methods from :class:`NeonStream`.
    """

    def __init__(self, file: Path):
        super().__init__(file)
        self.sampling_freq_nominal = int(110)
        self.data = self.data.astype(
            {
                "gyro x [deg/s]": float,
                "gyro y [deg/s]": float,
                "gyro z [deg/s]": float,
                "acceleration x [g]": float,
                "acceleration y [g]": float,
                "acceleration z [g]": float,
                "roll [deg]": float,
                "pitch [deg]": float,
                "yaw [deg]": float,
                "quaternion w": float,
                "quaternion x": float,
                "quaternion y": float,
                "quaternion z": float,
                "time [s]": float,
            }
        )


class CustomStream(NeonStream):
    """
    Custom stream data that inherits attributes and methods from :class:`NeonStream`.
    """

    def __init__(self, data: pd.DataFrame):
        self.file = None
        self.data = data
        self.sampling_freq_nominal = None
        self._get_attributes()
