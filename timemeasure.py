import time
import numpy as np


class MeasureTime:
    def __init__(self, verbose=False):
        self.last_time = None
        self.ts_number = 0
        self.timestamps = []
        self.timediff = []
        self.timestampnames = []
        self.verbose = verbose

    def reset(self):
        self.last_time = None
        self.ts_number = 0
        self.timestamps.clear()
        self.timediff.clear()

    def timestamp(self, name=None):
        if name is None:
            name = str(self.ts_number)

        act_time = time.time()
        self.timestamps.append(act_time)
        self.timestampnames.append(name)
        if self.last_time is not None:
            self.timediff.append(act_time - self.last_time)
            if self.verbose:
                print("TS:", name, act_time - self.last_time)
        self.last_time = act_time
        self.ts_number += 1

    def print_timestamps(self):
        last_t = 0
        for idx, t in enumerate(self.timestamps):
            print("TS:", self.timestampnames[idx], t - last_t)
            last_t = t

    def get_average_timediff(self):
        return np.average(self.timediff)

    def get_time_stats(self):
        mean = np.average(self.timediff)
        min = np.min(self.timediff)
        max = np.max(self.timediff)
        _25_quartile = np.percentile(self.timediff, 25)
        median = np.median(self.timediff)
        _75_quartile = np.percentile(self.timediff, 75)
        return mean, min, _25_quartile, median, _75_quartile, max

    def get_whole_time_span(self):
        if len(self.timestamps) > 0:
            return self.timestamps[-1] - self.timestamps[0]
        else:
            return 0
