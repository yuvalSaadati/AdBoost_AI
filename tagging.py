from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import re
from prompts import *

from model_wrapper import run_model
TEXT_CANDIDATES = ["ad", "Ad", "text", "Text",
                   "body", "Body", "description", "Description"]
CTR_CANDIDATES = ["CTR", 'ctr', 'Ctr']


def pick_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


async def tag_ads(df: pd.DataFrame) -> pd.DataFrame:
    """Pure sync function: takes a DF and returns DF with tag columns."""
    text_col = pick_col(df, TEXT_CANDIDATES)
    if text_col is None:
        raise ValueError(
            "Could not find an ad text column (e.g., 'text'/'description').")

    df = df.copy()
    df["ad_text"] = df[text_col].astype(str)

    # --- Tagging all features ---

    df["FeelingBase"] = df["ad_text"].apply(
        lambda ad: run_model(system_role_feeling_base,
                             user_role_feeling_base, ad, "Feeling base")
    )

    df["FreeOffers"] = df["ad_text"].apply(
        lambda ad: run_model(system_role_free_offers,
                             user_role_free_offers, ad, "Free Offers")
    )

    df["Quality"] = df["ad_text"].apply(
        lambda ad: run_model(system_role_quality,
                             user_role_quality, ad, "Quality")
    )

    df["ProductLineup"] = df["ad_text"].apply(
        lambda ad: run_model(system_role_product_lineup,
                             user_role_product_lineup, ad, "Product Lineup")
    )

    df["Speed"] = df["ad_text"].apply(
        lambda ad: run_model(system_role_speed, user_role_speed, ad, "Speed")
    )

    df["UserFriendliness"] = df["ad_text"].apply(
        lambda ad: run_model(system_role_user_friendliness,
                             user_role_user_friendliness, ad, "User Friendliness")
    )

    df["SocialIdentity"] = df["ad_text"].apply(
        lambda ad: run_model(system_role_social_identity,
                             user_role_social_identity, ad, "Social Identity")
    )

    df["ProductDescription"] = df["ad_text"].apply(
        lambda ad: run_model(system_role_product_description,
                             user_role_product_description, ad, "Product Description")
    )

    df["Motive"] = df["ad_text"].apply(
        lambda ad: run_model(system_role_motive,
                             user_role_motive, ad, "Motive")
    )

    df["Curiosity"] = df["ad_text"].apply(
        lambda ad: run_model(system_role_curiosity,
                             user_role_curiosity, ad, "Curiosity")
    )

    # --- Extra Feature: Personalization (detects "you" or "your") ---
    df["Personalization"] = df["ad_text"].apply(
        lambda ad: "Yes" if re.search(
            r"\byou(r)?\b", ad, flags=re.IGNORECASE) else "No"
    )

    return df
