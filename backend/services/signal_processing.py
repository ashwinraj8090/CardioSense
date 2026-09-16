"""
services/signal_processing.py
------------------------------
WHAT: Implements the exact HRV (RMSSD) and BP (PAT-based) formulas from
      your paper -- unchanged math, just moved from browser JavaScript to
      the backend, per your instruction ("prefer backend processing").
WHY:  The browser is not a trustworthy place for anything that feeds a
      security/health decision: a user could open devtools and set
      window.hr = 40 before it's sent, or simply edit the JS. Also,
      client-side state (rrIntervals, lastRPeakTime) was lost on every
      page refresh. Moving it here means the math is authoritative and
      survives reconnects, because it's tied to the session row in the
      database, not a browser tab.
WHERE THIS RUNS: called from routes/readings.py every time a sensor
      packet is authenticated and accepted.

Formulas (identical to the paper and to the original dashboard JS):
  ECG low-pass filter:   filtered(t) = a*raw(t) + (1-a)*filtered(t-1), a=0.3
  R-peak detection:      filtered crosses threshold AND >=400ms since last peak
  RR interval:           RR_i = t_i - t_(i-1)
  HRV (RMSSD):           sqrt( mean( (RR_i - RR_(i-1))^2 ) ), needs >=5 RR intervals
  PAT:                   |t_ppg_peak - t_ecg_rpeak|
  Systolic BP:           120 + (250 - PAT) * 0.15, clamped to [95, 175]
  Diastolic BP:          0.65 * Systolic
"""
import math
import time

ALPHA = 0.3
ECG_THRESHOLD = 2500
MIN_PEAK_GAP_MS = 400
PPG_THRESHOLD = 600
MAX_RR_HISTORY = 20


def process_sample(state: dict, ecg_value: float, ppg_value: float) -> dict:
    """
    Takes the session's current signal_state dict and one new (ecg, ppg)
    sample, returns an updated state PLUS this sample's derived hrv/bp
    (hrv/systolic/diastolic will be None if not enough data yet -- this
    mirrors the original dashboard's "return null, don't fake it" fix).
    """
    now_ms = time.time() * 1000

    filtered_ecg = state.get("filtered_ecg", 0.0)
    last_r_peak_time = state.get("last_r_peak_time", 0.0)
    last_ppg_peak_time = state.get("last_ppg_peak_time", 0.0)
    rr_intervals = state.get("rr_intervals", [])

    # 1. Low-pass filter the ECG sample
    filtered_ecg = ALPHA * ecg_value + (1 - ALPHA) * filtered_ecg

    # 2. R-peak detection -> RR interval bookkeeping
    if filtered_ecg > ECG_THRESHOLD and (now_ms - last_r_peak_time) > MIN_PEAK_GAP_MS:
        if last_r_peak_time > 0:
            rr_intervals.append(now_ms - last_r_peak_time)
            if len(rr_intervals) > MAX_RR_HISTORY:
                rr_intervals = rr_intervals[-MAX_RR_HISTORY:]
        last_r_peak_time = now_ms

    # 3. PPG peak detection (for PAT)
    if ppg_value > PPG_THRESHOLD and (now_ms - last_ppg_peak_time) > MIN_PEAK_GAP_MS:
        last_ppg_peak_time = now_ms

    # 4. HRV (RMSSD) -- only once we have enough intervals
    hrv = None
    if len(rr_intervals) >= 5:
        diffs_sq = [
            (rr_intervals[i] - rr_intervals[i - 1]) ** 2
            for i in range(1, len(rr_intervals))
        ]
        hrv = round(math.sqrt(sum(diffs_sq) / (len(rr_intervals) - 1)), 1)

    # 5. BP via PAT -- only meaningful once we've seen at least one R-peak and PPG peak
    systolic = diastolic = None
    if last_r_peak_time > 0 and last_ppg_peak_time > 0:
        pat = abs(last_ppg_peak_time - last_r_peak_time)
        sys_bp = 120 + (250 - pat) * 0.15
        sys_bp = max(95.0, min(175.0, sys_bp))
        systolic = round(sys_bp)
        diastolic = round(sys_bp * 0.65)

    new_state = {
        "filtered_ecg": filtered_ecg,
        "last_r_peak_time": last_r_peak_time,
        "last_ppg_peak_time": last_ppg_peak_time,
        "rr_intervals": rr_intervals,
    }

    return {
        "state": new_state,
        "hrv": hrv,
        "systolic": systolic,
        "diastolic": diastolic,
    }
