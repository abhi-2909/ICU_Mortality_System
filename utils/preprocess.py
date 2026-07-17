import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


def load_data(csv_path="dataset/icu_data.csv"):
    """
    Load ICU dataset
    """
    df = pd.read_csv(csv_path)

    print("=" * 50)
    print("Dataset Loaded Successfully")
    print("=" * 50)

    print("Shape :", df.shape)
    print()

    return df


def clean_data(df):
    """
    Basic preprocessing
    """

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Fill missing values
    for col in df.columns:

        if df[col].dtype == "object":
            df[col] = df[col].fillna(df[col].mode()[0])

        else:
            df[col] = df[col].fillna(df[col].median())

    return df


def encode_features(df):
    """
    Encode categorical features
    """

    encoder = LabelEncoder()

    df["gender"] = encoder.fit_transform(df["gender"])

    # Save encoder
    joblib.dump(
        encoder,
        "models/gender_encoder.pkl"
    )

    print("Gender Encoder Saved")

    return df


def split_dataset(df):

    X = df.drop("mortality", axis=1)

    y = df["mortality"]

    X_train, X_test, y_train, y_test = train_test_split(

        X,
        y,

        test_size=0.20,

        random_state=42,

        stratify=y

    )

    return X_train, X_test, y_train, y_test