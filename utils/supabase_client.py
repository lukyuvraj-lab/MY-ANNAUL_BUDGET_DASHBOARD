import os

import streamlit as st
from supabase import create_client


# =========================================================
# SUPABASE CONFIGURATION
# =========================================================
SUPABASE_URL = st.secrets.get(
    "SUPABASE_URL",
    os.getenv("SUPABASE_URL", "")
)

SUPABASE_KEY = st.secrets.get(
    "SUPABASE_KEY",
    os.getenv("SUPABASE_KEY", "")
)


# =========================================================
# VALIDATION
# =========================================================
if not SUPABASE_URL:
    raise RuntimeError(
        "SUPABASE_URL is missing. "
        "Add SUPABASE_URL to Streamlit secrets."
    )

if not SUPABASE_KEY:
     raise RuntimeError(
        "SUPABASE_KEY is missing. "
        "Add SUPABASE_KEY to Streamlit secrets."
    )


# =========================================================
# SUPABASE CLIENT
# =========================================================
supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)
