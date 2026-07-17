import pandas as pd


def create_features(df):
    """
    Create additional clinical features
    """

    # -------------------------------
    # Mean Arterial Pressure (MAP)
    # MAP = (SBP + 2*DBP) / 3
    # -------------------------------
    df["map"] = (
        df["systolic_bp"] +
        (2 * df["diastolic_bp"])
    ) / 3

    # -------------------------------
    # Pulse Pressure
    # -------------------------------
    df["pulse_pressure"] = (
        df["systolic_bp"] -
        df["diastolic_bp"]
    )

    # -------------------------------
    # Shock Index
    # Heart Rate / SBP
    # -------------------------------
    df["shock_index"] = (
        df["heart_rate"] /
        df["systolic_bp"]
    )

    # -------------------------------
    # BUN / Creatinine Ratio
    # -------------------------------
    df["bun_creatinine_ratio"] = (
        df["bun"] /
        (df["creatinine"] + 0.01)
    )

    # -------------------------------
    # Oxygen Deficit
    # -------------------------------
    df["oxygen_deficit"] = (
        100 -
        df["spo2"]
    )

    # -------------------------------
    # Elderly Flag
    # -------------------------------
    df["elderly"] = (
        df["age"] >= 65
    ).astype(int)

    return df