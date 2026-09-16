
import math
import time

ALPHA = 0.3
ECG_THRESHOLD = 2500
MIN_PEAK_GAP_MS = 400
PPG_THRESHOLD = 600
MAX_RR_HISTORY = 20


def process_sample(state: dict, ecg_value: float, ppg_value: float) -> dict:
   
    now_ms = time.time() * 1000

    filtered_ecg = state.get("filtered_ecg", 0.0)
    last_r_peak_time = state.get("last_r_peak_time", 0.0)
    last_ppg_peak_time = state.get("last_ppg_peak_time", 0.0)
    rr_intervals = state.get("rr_intervals", [])

    # 1. Low-pass filter the ECG sample
    filtered_ecg = ALPHA * ecg_value + (1 - ALPHA) * filtered_ecg

    # 2. R-peak detection 
    if filtered_ecg > ECG_THRESHOLD and (now_ms - last_r_peak_time) > MIN_PEAK_GAP_MS:
        if last_r_peak_time > 0:
            rr_intervals.append(now_ms - last_r_peak_time)
            if len(rr_intervals) > MAX_RR_HISTORY:
                rr_intervals = rr_intervals[-MAX_RR_HISTORY:]
        last_r_peak_time = now_ms

    # 3. PPG peak detection (for PAT)
    if ppg_value > PPG_THRESHOLD and (now_ms - last_ppg_peak_time) > MIN_PEAK_GAP_MS:
        last_ppg_peak_time = now_ms

    # 4. HRV (RMSSD) 
    hrv = None
    if len(rr_intervals) >= 5:
        diffs_sq = [
            (rr_intervals[i] - rr_intervals[i - 1]) ** 2
            for i in range(1, len(rr_intervals))
        ]
        hrv = round(math.sqrt(sum(diffs_sq) / (len(rr_intervals) - 1)), 1)

    # 5. BP via PAT 
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
