from google import genai
import streamlit as st
import pandas as pd


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="InsightIQ",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# SESSION STATE
# =========================================================

if "df" not in st.session_state:
    st.session_state.df = None
# Global Theme
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

if "table_rows" not in st.session_state:
    st.session_state.table_rows = 10

if "notifications" not in st.session_state:
    st.session_state.notifications = True

if "cleaning_summary" not in st.session_state:
    st.session_state.cleaning_summary = None

if "raw_df" not in st.session_state:
    st.session_state.raw_df = None


def show_success(message):
    """Display success messages when notifications are enabled."""
    if st.session_state.notifications:
        st.success(message)


def display_rows(data):
    """Limit table previews while allowing the user to display all rows."""
    if st.session_state.table_rows == "All":
        return data
    return data.head(int(st.session_state.table_rows))


def render_cleaning_view(data):
    """Show the dataset analysis/cleaning information after navigation."""

    st.subheader("Dataset Preview")
    st.dataframe(display_rows(data))

    st.subheader("📊 Dataset Overview")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Rows", data.shape[0])

    with col2:
        st.metric("Total Columns", data.shape[1])

    st.write("### 📋 Column Names")
    st.write(list(data.columns))

    st.write("### ❗ Missing Values")
    st.write(data.isnull().sum())

    st.write("### 🔤 Data Types")
    st.write(data.dtypes)

    numeric_columns = data.select_dtypes(
        include="number"
    ).columns.tolist()

    if numeric_columns:
        st.write("### 📈 Numeric Column Analysis")
        numeric_summary = data[numeric_columns].describe().T
        st.dataframe(display_rows(numeric_summary))

    if len(numeric_columns) >= 2:
        st.write("### 🔗 Correlation Analysis")
        correlation = data[numeric_columns].corr()
        st.dataframe(display_rows(correlation))

    categorical_columns = data.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    if categorical_columns:
        st.write("### 🏷️ Categorical Analysis")
        for column in categorical_columns:
            st.write(f"#### {column}")
            category_counts = data[column].value_counts().head(10)
            st.write(category_counts)

    st.write("### 🔢 Numeric Columns")
    st.write(numeric_columns)

    st.write("### 🏷️ Categorical Columns")
    st.write(categorical_columns)

    if categorical_columns:
        st.write("### 🧠 Smart Column Analysis")
        for column in categorical_columns:
            unique_count = data[column].nunique()
            total_rows = len(data)
            unique_percentage = (
                unique_count / total_rows
            ) * 100 if total_rows else 0

            st.write(f"#### {column}")
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Unique Values", unique_count)

            with col2:
                st.metric("Unique %", f"{unique_percentage:.2f}%")

            if unique_percentage <= 5:
                st.info("Low-cardinality categorical column")
                st.write("Top values:")
                st.write(data[column].value_counts().head(10))
            elif unique_percentage <= 50:
                st.info("Medium-cardinality column")
            else:
                st.warning(
                    "High-cardinality column — may be an identifier or free-text column."
                )

    st.write("### 🔁 Duplicate Rows")
    duplicate_rows = int(data.duplicated().sum())
    st.write("Number of duplicate rows:", duplicate_rows)

    st.write("### 📈 Missing Value Percentage")
    missing_percentage = (
        data.isnull().sum() / len(data) * 100
        if len(data) else data.isnull().sum()
    )
    st.write(
        missing_percentage.round(2).astype(str) + "%"
    )

    st.write("### ⚠️ High Missing Value Columns")
    high_missing_columns = missing_percentage[
        missing_percentage > 50
    ].index.tolist()
    st.write(high_missing_columns)


# =========================================================
# UI STYLING
# =========================================================

st.markdown(
    """
    <style>
    /* =====================================================
       INSIGHTIQ - POLISHED UI
       Presentation only: existing data/functions are preserved.
       ===================================================== */

    :root {
        --iq-navy: #172B4D;
        --iq-blue: #4F6FFF;
        --iq-blue-dark: #3157D5;
        --iq-purple: #7C4DFF;
        --iq-bg: #F5F8FF;
        --iq-card: #FFFFFF;
        --iq-border: #DCE6F7;
        --iq-text: #12233F;
        --iq-muted: #667797;
        --iq-green: #12B76A;
    }

    .stApp {
        background: linear-gradient(135deg, #F7FAFF 0%, #F3F6FD 55%, #EEF3FF 100%);
        color: var(--iq-text);
    }

    .block-container {
        max-width: 1480px;
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Top-level headings */
    .stApp h1 {
        color: var(--iq-text);
        font-size: 2.05rem !important;
        font-weight: 780 !important;
        letter-spacing: -0.7px;
        margin-bottom: 0.65rem;
    }

    .stApp h2 {
        color: var(--iq-text);
        font-size: 1.48rem !important;
        font-weight: 740 !important;
    }

    .stApp h3 {
        color: #20385F;
        font-size: 1.18rem !important;
        font-weight: 700 !important;
    }

    .stApp p, .stApp label {
        color: #334A70;
    }

    /* =====================================================
       SIDEBAR
       ===================================================== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #182E53 0%, #10213E 100%) !important;
        border-right: 0 !important;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.35rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }

    section[data-testid="stSidebar"] * {
        color: #F8FBFF !important;
    }

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1 {
        color: #FFFFFF !important;
        font-size: 1.75rem !important;
        margin-bottom: 0.2rem;
    }

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #C8D6EE !important;
        line-height: 1.45;
    }

    section[data-testid="stSidebar"] .stRadio > label {
        color: #BFD0EA !important;
        font-size: 0.82rem !important;
        font-weight: 650 !important;
        margin-bottom: 0.45rem !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 0.22rem;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        border-radius: 11px;
        padding: 9px 10px;
        margin: 2px 0;
        min-height: 40px;
        transition: all 0.18s ease;
        background: transparent;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(255,255,255,0.09);
        transform: translateX(2px);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, #4F6FFF 0%, #6C5CE7 100%) !important;
        box-shadow: 0 8px 20px rgba(79,111,255,0.30);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) * {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* =====================================================
       CARDS / METRICS
       ===================================================== */
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.96) !important;
        border: 1px solid var(--iq-border) !important;
        border-radius: 16px !important;
        padding: 17px 18px !important;
        box-shadow: 0 6px 22px rgba(35,73,145,0.075);
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 28px rgba(35,73,145,0.13);
    }

    div[data-testid="stMetricLabel"] {
        color: #647797 !important;
        font-weight: 650 !important;
        font-size: 0.86rem !important;
    }

    div[data-testid="stMetricValue"] {
        color: var(--iq-text) !important;
        font-weight: 800 !important;
        font-size: 1.65rem !important;
    }

    div[data-testid="stMetricDelta"] {
        color: #52698E !important;
    }

    /* Give the four main metric cards soft icon-like accent areas. */
    div[data-testid="stMetric"]:nth-of-type(1) {
        border-top: 3px solid #4F6FFF !important;
    }
    div[data-testid="stMetric"]:nth-of-type(2) {
        border-top: 3px solid #2FA7E0 !important;
    }
    div[data-testid="stMetric"]:nth-of-type(3) {
        border-top: 3px solid #7C4DFF !important;
    }
    div[data-testid="stMetric"]:nth-of-type(4) {
        border-top: 3px solid #E83E8C !important;
    }

    /* =====================================================
       BUTTONS
       ===================================================== */
    .stButton > button,
    .stDownloadButton > button {
        border-radius: 11px !important;
        min-height: 43px;
        padding: 0.45rem 1rem !important;
        font-weight: 700 !important;
        border: 1px solid #C9D8F5 !important;
        background: #FFFFFF !important;
        color: #17356D !important;
        box-shadow: 0 3px 10px rgba(40,80,160,0.06);
        transition: all 0.18s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        border-color: #9FB8F5 !important;
        background: #F4F7FF !important;
        box-shadow: 0 8px 18px rgba(55,93,190,0.14);
    }

    /* Primary-looking action buttons */
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(90deg, #4F6FFF, #665BEA) !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 8px 18px rgba(79,111,255,0.22);
    }

    /* =====================================================
       INPUTS / SELECTS
       ===================================================== */
    div[data-baseweb="select"] > div,
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {
        border-radius: 11px !important;
        border-color: #D6E1F2 !important;
        background: #FFFFFF !important;
    }

    div[data-baseweb="select"] > div:hover {
        border-color: #9DB5EE !important;
    }

    /* =====================================================
       FILE UPLOADER
       ===================================================== */
    section[data-testid="stFileUploaderDropzone"] {
        background: linear-gradient(135deg, #F9FBFF, #F2F6FF) !important;
        border: 1px dashed #AFC3EC !important;
        border-radius: 14px !important;
        padding: 0.8rem !important;
    }

    section[data-testid="stFileUploaderDropzone"]:hover {
        background: #EEF4FF !important;
        border-color: #6485EA !important;
    }

    section[data-testid="stFileUploaderDropzone"] button {
        border-radius: 9px !important;
        background: #FFFFFF !important;
        color: #17356D !important;
        border: 1px solid #BFD0ED !important;
    }

    section[data-testid="stFileUploaderDropzone"] button:hover {
        background: #EEF4FF !important;
        color: #17356D !important;
    }

    /* =====================================================
       DATAFRAMES / EXPANDERS / ALERTS
       ===================================================== */
    div[data-testid="stDataFrame"] {
        border: 1px solid #D9E3F3 !important;
        border-radius: 13px !important;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(30,64,175,0.055);
    }

    div[data-testid="stExpander"] {
        border: 1px solid #D9E3F3 !important;
        border-radius: 13px !important;
        background: rgba(255,255,255,0.80);
    }

    div[data-testid="stAlert"] {
        border-radius: 11px !important;
    }

    hr {
        border-color: #DCE5F3 !important;
        margin: 1.1rem 0 !important;
    }

    /* =====================================================
       HOME HERO / CUSTOM UI
       ===================================================== */
    .iq-hero {
        background: linear-gradient(135deg, #EEF4FF 0%, #F8FAFF 55%, #E9EEFF 100%);
        border: 1px solid #D9E4FA;
        border-radius: 20px;
        padding: 24px 28px;
        margin: 0.2rem 0 1.25rem 0;
        box-shadow: 0 8px 26px rgba(58,88,160,0.08);
    }

    .iq-hero-title {
        font-size: 2rem;
        font-weight: 800;
        color: #12233F;
        margin: 0;
    }

    .iq-hero-title span {
        color: #4F6FFF;
    }

    .iq-hero-subtitle {
        color: #4D648C;
        font-size: 1rem;
        margin-top: 7px;
    }

    .iq-section-card {
        background: #FFFFFF;
        border: 1px solid #DCE6F7;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 5px 18px rgba(35,73,145,0.065);
    }

    .iq-section-title {
        color: #172B4D;
        font-size: 1.05rem;
        font-weight: 750;
        margin-bottom: 8px;
    }

    .iq-muted {
        color: #6B7F9F;
        font-size: 0.88rem;
    }

    .iq-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 42px;
        height: 42px;
        border-radius: 12px;
        margin-right: 9px;
        vertical-align: middle;
        font-size: 1.25rem;
    }

    .iq-icon-blue { background: #E8F0FF; }
    .iq-icon-cyan { background: #E5F7FF; }
    .iq-icon-purple { background: #F0E9FF; }
    .iq-icon-pink { background: #FFEAF3; }
    .iq-icon-green { background: #E8F8EF; }

    .iq-footer {
        margin-top: 1.2rem;
        background: linear-gradient(90deg, #EEF2FF, #F7F9FF);
        border: 1px solid #DDE5F7;
        border-radius: 15px;
        padding: 16px 20px;
        color: #4B6190;
        font-style: italic;
    }

    /* =====================================================
       DARK MODE
       ===================================================== */
    .iq-dark {
        color: #F5F7FB;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# Dark mode keeps the same visual language but uses dark surfaces.
if st.session_state.theme == "Dark":
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #0B1020 0%, #0F172A 60%, #111827 100%) !important;
            color: #F8FAFC !important;
        }

        .stApp h1, .stApp h2, .stApp h3, .stApp h4,
        .stApp h5, .stApp h6, .stApp p, .stApp label {
            color: #F8FAFC !important;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #142746 0%, #0B172D 100%) !important;
        }

        div[data-testid="stMetric"] {
            background: #151D2D !important;
            border-color: #2A3A56 !important;
            box-shadow: 0 8px 22px rgba(0,0,0,0.25);
        }

        div[data-testid="stMetricLabel"] {
            color: #AAB8D0 !important;
        }

        div[data-testid="stMetricValue"] {
            color: #F8FAFC !important;
        }

        .stButton > button,
        .stDownloadButton > button {
            background: #182337 !important;
            color: #F8FAFC !important;
            border-color: #334563 !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            background: #22314B !important;
            border-color: #5E7DCA !important;
        }

        div[data-testid="stButton"] button[kind="primary"] {
            background: linear-gradient(90deg, #4F6FFF, #7057E8) !important;
            color: #FFFFFF !important;
        }

        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input {
            background: #182337 !important;
            color: #F8FAFC !important;
            border-color: #334563 !important;
        }

        section[data-testid="stFileUploaderDropzone"] {
            background: #182337 !important;
            border-color: #405474 !important;
        }

        section[data-testid="stFileUploaderDropzone"] button {
            background: #FFFFFF !important;
            color: #17356D !important;
            border-color: #CBD7EA !important;
        }

        section[data-testid="stFileUploaderDropzone"] button:hover {
            background: #EAF0FF !important;
            color: #17356D !important;
        }

        div[data-testid="stDataFrame"] {
            border-color: #2A3A56 !important;
        }

        div[data-testid="stExpander"] {
            background: #151D2D !important;
            border-color: #2A3A56 !important;
        }

        .iq-hero {
            background: linear-gradient(135deg, #172541, #151D31) !important;
            border-color: #2C3E5C !important;
        }

        .iq-hero-title,
        .iq-section-title {
            color: #F8FAFC !important;
        }

        .iq-hero-subtitle,
        .iq-muted {
            color: #AEBBD0 !important;
        }

        .iq-section-card {
            background: #151D2D !important;
            border-color: #2A3A56 !important;
        }

        .iq-footer {
            background: #151D2D !important;
            border-color: #2A3A56 !important;
            color: #AEBBD0 !important;
        }

        hr {
            border-color: #2A3A56 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# APPLICATION TITLE
# =========================================================

st.markdown(
    """
    <div style="
        color:#6B7F9F;
        font-size:0.82rem;
        margin-top:-0.35rem;
        margin-bottom:0.8rem;
    ">
        AI-Powered Data Analytics Platform
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("📊 InsightIQ")
st.sidebar.write("AI-Powered Data Analytics Platform")

selected = st.sidebar.radio(
    "Menu",
    [
        "Home",
        "📂 Upload Dataset",
        "📊 Dashboard",
        "🤖 AI Insights",
        "📄 Reports",
        "⚙️ Settings"
    ]
)


# =========================================================
# =========================================================
# HOME
# =========================================================

if selected == "Home":

    # ---------------------------------------------------------
    # HERO
    # ---------------------------------------------------------

    st.markdown(
        """
        <div class="iq-hero">
            <div class="iq-hero-title"> Welcome to <span>InsightIQ</span></div>
            <div class="iq-hero-subtitle">
                Upload, explore, visualize and get AI-powered insights from your data.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    home_df = st.session_state.df

    if home_df is not None:

        numeric_home = home_df.select_dtypes(
            include="number"
        ).columns.tolist()

        categorical_home = home_df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        # -----------------------------------------------------
        # KPI CARDS
        # -----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                '<span class="iq-icon iq-icon-blue">🗄️</span>',
                unsafe_allow_html=True
            )
            st.metric("Total Rows", f"{home_df.shape[0]:,}")

        with col2:
            st.markdown(
                '<span class="iq-icon iq-icon-cyan">▦</span>',
                unsafe_allow_html=True
            )
            st.metric("Total Columns", home_df.shape[1])

        with col3:
            st.markdown(
                '<span class="iq-icon iq-icon-purple">▥</span>',
                unsafe_allow_html=True
            )
            st.metric("Numeric Columns", len(numeric_home))

        with col4:
            st.markdown(
                '<span class="iq-icon iq-icon-pink">◔</span>',
                unsafe_allow_html=True
            )
            st.metric("Categorical Columns", len(categorical_home))

        st.write("")

        # -----------------------------------------------------
        # PREVIEW + DATA OVERVIEW
        # -----------------------------------------------------

        left, right = st.columns([1.05, 0.95], gap="large")

        with left:

            st.markdown(
                """
                <div class="iq-section-card">
                    <div class="iq-section-title">
                        <span class="iq-icon iq-icon-blue">▦</span>
                        Dataset Preview
                    </div>
                    <div class="iq-muted">
                        Here's a quick look at your cleaned dataset.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.dataframe(
                display_rows(home_df),
                use_container_width=True
            )

        with right:

            st.markdown(
                """
                <div class="iq-section-card">
                    <div class="iq-section-title">
                        <span class="iq-icon iq-icon-purple">▥</span>
                        Data Overview
                    </div>
                    <div class="iq-muted">
                        Understand your dataset at a glance.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if categorical_home:

                overview_column = st.selectbox(
                    "Explore a categorical column",
                    categorical_home,
                    key="home_overview_column"
                )

                overview_counts = (
                    home_df[overview_column]
                    .value_counts()
                    .head(5)
                )

                st.bar_chart(
                    overview_counts,
                    use_container_width=True
                )

            elif numeric_home:

                overview_column = st.selectbox(
                    "Explore a numeric column",
                    numeric_home,
                    key="home_overview_numeric"
                )

                st.line_chart(
                    home_df[overview_column]
                    .reset_index(drop=True)
                )

            else:
                st.info("No suitable columns are available for a quick overview.")

        st.write("")

        # -----------------------------------------------------
        # DATA QUALITY + QUICK ACTIONS
        # -----------------------------------------------------

        quality_col, action_col = st.columns([1, 1], gap="large")

        with quality_col:

            duplicate_home = int(home_df.duplicated().sum())
            missing_home = int(home_df.isnull().sum().sum())

            st.markdown(
                """
                <div class="iq-section-card">
                    <div class="iq-section-title">
                        <span class="iq-icon iq-icon-green">🛡️</span>
                        Data Quality
                    </div>
                    <div class="iq-muted">
                        Check the quality of your cleaned dataset.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            q1, q2 = st.columns(2)

            with q1:
                if missing_home == 0:
                    st.success("🟢 Missing Values\n\n0")
                else:
                    st.warning(
                        f"🟠 Missing Values\n\n{missing_home:,}"
                    )

            with q2:
                if duplicate_home == 0:
                    st.success("🔵 Duplicate Rows\n\n0")
                else:
                    st.warning(
                        f"🟠 Duplicate Rows\n\n{duplicate_home:,}"
                    )

        with action_col:

            st.markdown(
                """
                <div class="iq-section-card">
                    <div class="iq-section-title">
                        <span class="iq-icon iq-icon-purple">⚡</span>
                        Quick Actions
                    </div>
                    <div class="iq-muted">
                        Continue working with your dataset.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            a1, a2 = st.columns(2)

            with a1:
                st.info("📂 Upload Dataset\n\nUse the menu to upload another CSV.")

            with a2:
                st.info("📊 Dashboard\n\nExplore KPIs and visualizations.")

        # -----------------------------------------------------
        # FOOTER
        # -----------------------------------------------------

        st.markdown(
            """
            <div class="iq-footer">
                💡 <b>“Data is not just numbers, it’s a story waiting to be told.”</b>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
            <div class="iq-section-card">
                <div class="iq-section-title">
                    <span class="iq-icon iq-icon-blue">📂</span>
                    Start with your dataset
                </div>
                <div class="iq-muted">
                    Upload a CSV dataset to clean, analyze, visualize and generate
                    AI-powered insights.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")
        st.info("📂 Go to **Upload Dataset** from the sidebar to get started.")

# =========================================================
# UPLOAD DATASET
# =========================================================

elif selected == "📂 Upload Dataset":

    st.title("📂 Upload Dataset")

    uploaded_file = st.file_uploader(
        "Upload your CSV dataset",
        type=["csv"]
    )

    if uploaded_file is not None:

        # Read CSV file
        df = pd.read_csv(uploaded_file)

        # Replace common missing-value placeholders
        df = df.replace(
            ["None", "none", "N/A", "NA", "null", "NULL", ""],
            pd.NA
        )

        # Store the pre-cleaning dataset so the complete analysis view
        # remains available after navigating to other sections.
        st.session_state.raw_df = df.copy()

        original_rows = int(df.shape[0])
        original_columns = int(df.shape[1])
        duplicates_detected = int(df.duplicated().sum())
        duplicate_rows_removed = 0
        high_missing_detected = []
        high_missing_removed = []
        missing_values_before_fill = int(df.isnull().sum().sum())
        missing_values_by_column = {
            column: int(value)
            for column, value in df.isnull().sum().items()
            if value > 0
        }
        data_types_before_cleaning = {
            column: str(dtype)
            for column, dtype in df.dtypes.items()
        }

        st.subheader("Dataset Preview")
        st.dataframe(display_rows(df))

        # -------------------------------------------------
        # DATASET OVERVIEW
        # -------------------------------------------------

        st.subheader("📊 Dataset Overview")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Total Rows",
                df.shape[0]
            )

        with col2:
            st.metric(
                "Total Columns",
                df.shape[1]
            )

        st.write("### 📋 Column Names")
        st.write(list(df.columns))

        # -------------------------------------------------
        # MISSING VALUES
        # -------------------------------------------------

        st.write("### ❗ Missing Values")

        missing_values = df.isnull().sum()

        st.write(missing_values)

        # -------------------------------------------------
        # DATA TYPES
        # -------------------------------------------------

        st.write("### 🔤 Data Types")

        st.write(df.dtypes)

        # -------------------------------------------------
        # AUTOMATIC COLUMN TYPE DETECTION
        # -------------------------------------------------

        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        # -------------------------------------------------
        # NUMERIC ANALYSIS
        # -------------------------------------------------

        if numeric_columns:

            st.write("### 📈 Numeric Column Analysis")

            numeric_summary = df[numeric_columns].describe().T

            st.dataframe(display_rows(numeric_summary))

        # -------------------------------------------------
        # CORRELATION ANALYSIS
        # -------------------------------------------------

        if len(numeric_columns) >= 2:

            st.write("### 🔗 Correlation Analysis")

            correlation = df[numeric_columns].corr()

            st.dataframe(display_rows(correlation))

        # -------------------------------------------------
        # CATEGORICAL ANALYSIS
        # -------------------------------------------------

        categorical_columns = df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        if categorical_columns:

            st.write("### 🏷️ Categorical Analysis")

            for column in categorical_columns:

                st.write(f"#### {column}")

                category_counts = (
                    df[column]
                    .value_counts()
                    .head(10)
                )

                st.write(category_counts)

        # -------------------------------------------------
        # COLUMN TYPES
        # -------------------------------------------------

        st.write("### 🔢 Numeric Columns")
        st.write(numeric_columns)

        st.write("### 🏷️ Categorical Columns")
        st.write(categorical_columns)

        # -------------------------------------------------
        # SMART COLUMN ANALYSIS
        # -------------------------------------------------

        if categorical_columns:

            st.write("### 🧠 Smart Column Analysis")

            for column in categorical_columns:

                unique_count = df[column].nunique()

                total_rows = len(df)

                unique_percentage = (
                    unique_count / total_rows
                ) * 100

                st.write(f"#### {column}")

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Unique Values",
                        unique_count
                    )

                with col2:

                    st.metric(
                        "Unique %",
                        f"{unique_percentage:.2f}%"
                    )

                if unique_percentage <= 5:

                    st.success(
                        "✅ Low-cardinality categorical column"
                    )

                    st.write("Top values:")

                    st.write(
                        df[column]
                        .value_counts()
                        .head(10)
                    )

                elif unique_percentage <= 50:

                    st.info(
                        "ℹ️ Medium-cardinality column"
                    )

                else:

                    st.warning(
                        "⚠️ High-cardinality column — "
                        "may be an identifier or free-text column."
                    )

        # -------------------------------------------------
        # DUPLICATE ROWS
        # -------------------------------------------------

        st.write("### 🔁 Duplicate Rows")

        duplicate_rows = int(df.duplicated().sum())

        st.write(
            "Number of duplicate rows:",
            duplicate_rows
        )

        if duplicate_rows > 0:

            st.warning(
                "Duplicate rows found in the dataset."
            )

            remove_duplicates = st.checkbox(
                "Remove duplicate rows"
            )

            if remove_duplicates:

                df = df.drop_duplicates()
                duplicate_rows_removed = duplicates_detected

                show_success("Duplicate rows removed successfully.")

        # -------------------------------------------------
        # MISSING VALUE PERCENTAGE
        # -------------------------------------------------

        missing_percentage = (
            df.isnull().sum() / len(df)
        ) * 100

        st.write("### 📈 Missing Value Percentage")

        st.write(
            missing_percentage
            .round(2)
            .astype(str)
            + "%"
        )

        # -------------------------------------------------
        # HIGH MISSING VALUE COLUMNS
        # -------------------------------------------------

        high_missing_columns = missing_percentage[
            missing_percentage > 50
        ].index.tolist()
        high_missing_detected = list(high_missing_columns)

        st.write("### ⚠️ High Missing Value Columns")

        st.write(high_missing_columns)

        if high_missing_columns:

            st.warning(
                "Some columns have more than 50% missing values."
            )

            remove_columns = st.checkbox(
                "Remove high-missing columns"
            )

            if remove_columns:

                df = df.drop(
                    columns=high_missing_columns
                )
                high_missing_removed = list(high_missing_columns)

                show_success("High-missing columns removed successfully.")

        # -------------------------------------------------
        # HANDLE REMAINING MISSING VALUES
        # -------------------------------------------------

        for column in df.columns:

            if df[column].isnull().sum() > 0:

                if pd.api.types.is_numeric_dtype(
                    df[column]
                ):

                    df[column] = df[column].fillna(
                        df[column].median()
                    )

                else:

                    df[column] = df[column].fillna(
                        "Unknown"
                    )

        show_success("Missing values handled successfully.")

        # -------------------------------------------------
        # FINAL CLEANED DATASET
        # -------------------------------------------------
        st.session_state.df = df

        st.session_state.cleaning_summary = {
            "original_rows": original_rows,
            "original_columns": original_columns,
            "duplicate_rows_detected": duplicates_detected,
            "duplicate_rows_removed": duplicate_rows_removed,
            "high_missing_columns_detected": high_missing_detected,
            "high_missing_columns_removed": high_missing_removed,
            "missing_values_before_fill": missing_values_before_fill,
            "missing_values_by_column": missing_values_by_column,
            "data_types_before_cleaning": data_types_before_cleaning,
            "final_rows": int(df.shape[0]),
            "final_columns": int(df.shape[1]),
            "missing_values_after_cleaning": int(df.isnull().sum().sum())
        }

        # -------------------------------------------------
        # CLEANING SUMMARY + DETAILS
        # -------------------------------------------------
        summary = st.session_state.cleaning_summary

        st.write("### 🧹 Cleaning Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Original Rows", summary["original_rows"])

        with col2:
            st.metric("Duplicates Removed", summary["duplicate_rows_removed"])

        with col3:
            st.metric("Missing Values Before", summary["missing_values_before_fill"])

        with col4:
            st.metric("Final Rows", summary["final_rows"])

        if summary.get("high_missing_columns_removed", []):
            st.write(
                "**High-missing columns removed:** "
                + ", ".join(summary.get("high_missing_columns_removed", []))
            )

        show_success(
            f"Cleaning completed: {summary['final_rows']} rows and "
            f"{summary['final_columns']} columns are ready for analysis."
        )

        with st.expander("🔍 View Cleaning Details", expanded=False):
            st.write("#### 1. Data Quality Check")
            st.write(
                f"Detected **{summary.get("duplicate_rows_detected", 0)} duplicate rows** "
                f"and **{summary["missing_values_before_fill"]} missing values** before cleaning."
            )

            if summary.get("missing_values_by_column", {}):
                st.write("**Missing values by column:**")
                st.dataframe(
                    pd.Series(
                        summary.get("missing_values_by_column", {}),
                        name="Missing Values"
                    ).to_frame()
                )
            else:
                st.write("No missing values were detected before cleaning.")

            st.write("#### 2. Duplicate Handling")
            if summary["duplicate_rows_removed"] > 0:
                st.write(
                    f"Detected {summary.get("duplicate_rows_detected", 0)} duplicate rows "
                    f"and removed {summary["duplicate_rows_removed"]}."
                )
            else:
                st.write("No duplicate rows were removed.")

            st.write("#### 3. High-Missing Columns")
            if summary.get("high_missing_columns_detected", []):
                st.write(
                    "Columns above the 50% missing-value threshold: "
                    + ", ".join(summary.get("high_missing_columns_detected", []))
                )
                if summary.get("high_missing_columns_removed", []):
                    st.write(
                        "Removed columns: "
                        + ", ".join(summary.get("high_missing_columns_removed", []))
                    )
                else:
                    st.write("No high-missing columns were removed.")
            else:
                st.write("No columns exceeded the 50% missing-value threshold.")

            st.write("#### 4. Missing Value Handling")
            st.write(
                "Numeric missing values were filled using the column median, "
                "while categorical/text missing values were filled with `Unknown`."
            )
            st.write(
                f"Missing values after cleaning: **{summary.get("missing_values_after_cleaning", 0)}**"
            )

            st.write("#### 5. Final Result")
            st.write(
                f"The cleaned dataset contains **{summary["final_rows"]} rows** "
                f"and **{summary["final_columns"]} columns** and is ready for analysis."
            )

    elif st.session_state.df is not None:

        st.info(
            "A cleaned dataset is already available. The cleaning analysis is preserved below."
        )

        # Show the same analysis view that was displayed during upload.
        if st.session_state.raw_df is not None:
            render_cleaning_view(st.session_state.raw_df)

        # -------------------------------------------------
        # CLEANING SUMMARY
        # -------------------------------------------------
        if st.session_state.cleaning_summary is not None:
            summary = st.session_state.cleaning_summary

            st.write("### 🧹 Cleaning Summary")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Original Rows", summary["original_rows"])

            with col2:
                st.metric("Duplicates Removed", summary["duplicate_rows_removed"])

            with col3:
                st.metric("Missing Values Before", summary["missing_values_before_fill"])

            with col4:
                st.metric("Final Rows", summary["final_rows"])

            if summary.get("high_missing_columns_removed", []):
                st.write(
                    "**High-missing columns removed:** "
                    + ", ".join(summary["high_missing_columns_removed"])
                )

            show_success(
                f"Cleaning completed: {summary['final_rows']} rows and "
                f"{summary['final_columns']} columns are ready for analysis."
            )

        st.write("### 🧹 Final Cleaned Dataset")
        st.dataframe(display_rows(st.session_state.df))



# =========================================================
# DASHBOARD
# =========================================================

elif selected == "📊 Dashboard":

    st.title("📊 Dashboard")

    if st.session_state.df is not None:

        dashboard_df = st.session_state.df

        st.write("### 📊 Dataset Overview")

        # -------------------------------------------------
        # AUTOMATIC COLUMN DETECTION
        # -------------------------------------------------

        numeric_columns = dashboard_df.select_dtypes(
            include="number"
        ).columns.tolist()

        categorical_columns = dashboard_df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        # -------------------------------------------------
        # KPI CARDS
        # -------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Total Rows",
                dashboard_df.shape[0]
            )

        with col2:

            st.metric(
                "Total Columns",
                dashboard_df.shape[1]
            )

        with col3:

            st.metric(
                "Numeric Columns",
                len(numeric_columns)
            )

        with col4:

            st.metric(
                "Categorical Columns",
                len(categorical_columns)
            )

        # -------------------------------------------------
        # DATA VISUALIZATION
        # -------------------------------------------------

        st.write("### 📊 Data Visualization")

        # -------------------------------------------------
        # CATEGORICAL VISUALIZATION
        # -------------------------------------------------

        if categorical_columns:

            st.write("#### 🏷️ Categorical Distribution")

            selected_category = st.selectbox(
                "Select a categorical column",
                categorical_columns
            )

            category_counts = (
                dashboard_df[selected_category]
                .value_counts()
                .head(10)
            )

            st.bar_chart(category_counts)

        # -------------------------------------------------
        # NUMERIC VISUALIZATION
        # -------------------------------------------------

        if numeric_columns:

            st.write("#### 📈 Numeric Distribution")

            # Detect numeric columns that are likely
            # identifiers or codes

            identifier_keywords = [
                "id",
                "code",
                "zip",
                "postal",
                "pincode",
                "pin_code",
                "phone",
                "mobile"
            ]

            identifier_columns = []

            for column in numeric_columns:

                column_name = (
                    column
                    .lower()
                    .replace(" ", "_")
                )

                if any(
                    keyword in column_name
                    for keyword in identifier_keywords
                ):

                    identifier_columns.append(
                        column
                    )

            # Keep only meaningful numeric columns
            # for visualization

            meaningful_numeric_columns = [
                column
                for column in numeric_columns
                if column not in identifier_columns
            ]

            if meaningful_numeric_columns:

                selected_numeric = st.selectbox(
                    "Select a numeric column",
                    meaningful_numeric_columns
                )

                st.line_chart(
                    dashboard_df[selected_numeric]
                    .reset_index(drop=True)
                )

            elif identifier_columns:

                st.info(
                    "No meaningful numerical columns are "
                    "available for distribution visualization. "
                    "Identifier/code columns such as "
                    + ", ".join(identifier_columns)
                    + " were excluded."
                )

    else:

        st.info(
            "Please upload a dataset first."
        )


# =========================================================
# AI INSIGHTS
# =========================================================

elif selected == "🤖 AI Insights":

    st.title("🤖 AI Insights")

    if st.session_state.df is not None:

        df = st.session_state.df

        st.write(
            "Generate AI-powered insights from your cleaned dataset."
        )

        # -------------------------------------------------
        # DATASET SUMMARY
        # -------------------------------------------------

        st.write("### 📊 Dataset Summary")

        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        categorical_columns = df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Total Rows",
                df.shape[0]
            )

        with col2:

            st.metric(
                "Total Columns",
                df.shape[1]
            )

        with col3:

            st.metric(
                "Numeric Columns",
                len(numeric_columns)
            )

        with col4:

            st.metric(
                "Categorical Columns",
                len(categorical_columns)
            )

        # -------------------------------------------------
        # DATA QUALITY
        # -------------------------------------------------

        st.write("### 🔍 Data Quality")

        duplicate_rows = int(
            df.duplicated().sum()
        )

        missing_values = int(
            df.isnull().sum().sum()
        )

        col1, col2 = st.columns(2)

        with col1:

            if duplicate_rows == 0:

                st.success(
                    "✅ No duplicate rows found."
                )

            else:

                st.warning(
                    f"⚠️ {duplicate_rows} duplicate rows found."
                )

        with col2:

            if missing_values == 0:

                st.success(
                    "✅ No missing values found."
                )

            else:

                st.warning(
                    f"⚠️ {missing_values} missing values found."
                )

        # -------------------------------------------------
        # STATISTICAL SUMMARY
        # -------------------------------------------------

        st.write("### 📈 Statistical Summary")

        statistics = {}

        for column in numeric_columns:

            statistics[column] = {

                "mean": float(
                    df[column].mean()
                ),

                "median": float(
                    df[column].median()
                ),

                "minimum": float(
                    df[column].min()
                ),

                "maximum": float(
                    df[column].max()
                ),

                "std": float(
                    df[column].std()
                )
            }

        if statistics:

            st.json(statistics)

        # -------------------------------------------------
        # CATEGORICAL SUMMARY
        # -------------------------------------------------

        categorical_summary = {}

        for column in categorical_columns:

            unique_count = int(
                df[column].nunique()
            )

            top_values = (
                df[column]
                .value_counts()
                .head(5)
                .to_dict()
            )

            categorical_summary[column] = {

                "unique_values": unique_count,

                "top_values": top_values
            }

        # -------------------------------------------------
        # GENERATE AI INSIGHTS
        # -------------------------------------------------

        st.write("### 🤖 Gemini AI Analysis")

        if st.button(
            "✨ Generate AI Insights",
            use_container_width=True
        ):

            try:

                # Get API key from Streamlit secrets

                api_key = st.secrets[
                    "GEMINI_API_KEY"
                ]

                client = genai.Client(
                    api_key=api_key
                )

                # -----------------------------------------
                # CREATE COMPACT DATA SUMMARY
                # -----------------------------------------

                dataset_summary = {

                    "rows": int(
                        df.shape[0]
                    ),

                    "columns": int(
                        df.shape[1]
                    ),

                    "column_names":
                        df.columns.tolist(),

                    "numeric_columns":
                        numeric_columns,

                    "categorical_columns":
                        categorical_columns,

                    "duplicate_rows":
                        duplicate_rows,

                    "missing_values":
                        missing_values,

                    "numeric_statistics":
                        statistics,

                    "categorical_summary":
                        categorical_summary
                }

                # -----------------------------------------
                # GEMINI PROMPT
                # -----------------------------------------

                prompt = f"""
You are a senior data analyst.

Analyze the following dataset summary and generate
clear, practical and concise business/data insights.

IMPORTANT:
- Do not invent facts.
- Use only the information provided below.
- Clearly distinguish observations from recommendations.
- Do not mention information that is not present.
- Keep the language simple and professional.

Dataset Summary:
{dataset_summary}

Provide the analysis in exactly these sections:

1. 🔎 Key Findings
- Mention the most important patterns or observations.

2. ⚠️ Important Data Issues
- Mention missing values, duplicates, high-cardinality columns,
  unusual distributions or possible identifier columns.

3. 📊 Statistical Insights
- Explain meaningful numerical patterns.

4. 💡 Recommendations
- Give practical recommendations for further analysis
  or data usage.

5. 📝 Overall Summary
- Give a short overall conclusion about the dataset.
"""

                with st.spinner(
                    "🤖 Gemini is analyzing your dataset..."
                ):

                    interaction = client.interactions.create(
                        model="gemini-3.5-flash-lite",
                        input=prompt
                    )

                    ai_response = (
                        interaction.output_text
                    )

                show_success("✅ AI insights generated successfully!")

                st.markdown(ai_response)

            except KeyError:

                st.error(
                    "❌ GEMINI_API_KEY not found. "
                    "Please check your .streamlit/secrets.toml file."
                )

            except Exception as e:

                st.error(
                    f"❌ Gemini API error: {e}"
                )

    else:

        st.info(
            "Please upload a dataset first."
        )
# =========================================================
# REPORTS
# =========================================================

elif selected == "📄 Reports":

    st.title("📄 Reports")

    if st.session_state.df is not None:

        df = st.session_state.df

        st.write("### 📑 Dataset Report")

        st.write(
            "Download the cleaned dataset and a formatted analysis report."
        )

        # -------------------------------------------------
        # CLEANED DATASET DOWNLOAD
        # -------------------------------------------------

        st.write("#### 🧹 Cleaned Dataset")

        csv_data = df.to_csv(index=False)

        st.download_button(
            label="⬇️ Download Cleaned Dataset",
            data=csv_data,
            file_name="cleaned_dataset.csv",
            mime="text/csv"
        )

        # -------------------------------------------------
        # HTML ANALYSIS REPORT
        # -------------------------------------------------

        st.write("#### 📊 Analysis Report")

        # Missing values
        missing_values = df.isnull().sum()

        missing_html = ""

        for column, value in missing_values.items():

            missing_html += f"""
            <tr>
                <td>{column}</td>
                <td>{value}</td>
            </tr>
            """

        # Numeric columns
        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        numeric_html = ""

        for column in numeric_columns:
            numeric_html += f"<li>{column}</li>"

        if not numeric_html:
            numeric_html = "<li>No numerical columns found.</li>"

        # Categorical columns
        categorical_columns = df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        categorical_html = ""

        for column in categorical_columns:
            categorical_html += f"<li>{column}</li>"

        if not categorical_html:
            categorical_html = "<li>No categorical columns found.</li>"

        # Column names
        column_html = ""

        for column in df.columns:
            column_html += f"<li>{column}</li>"

        # -------------------------------------------------
        # CREATE HTML REPORT
        # -------------------------------------------------

        report_html = f"""
        <!DOCTYPE html>

        <html>

        <head>

            <meta charset="UTF-8">

            <title>InsightIQ - Data Analysis Report</title>

            <style>

                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f5f7fa;
                    color: #1f2937;
                    margin: 0;
                    padding: 40px;
                }}

                .container {{
                    max-width: 900px;
                    margin: auto;
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                }}

                h1 {{
                    color: #1f2937;
                    margin-bottom: 5px;
                }}

                .subtitle {{
                    color: #6b7280;
                    margin-bottom: 30px;
                }}

                h2 {{
                    margin-top: 35px;
                    border-bottom: 2px solid #e5e7eb;
                    padding-bottom: 8px;
                }}

                .summary {{
                    display: flex;
                    gap: 20px;
                    margin: 20px 0;
                }}

                .card {{
                    flex: 1;
                    background: #f8fafc;
                    border: 1px solid #e5e7eb;
                    padding: 20px;
                    border-radius: 10px;
                }}

                .card-title {{
                    font-size: 14px;
                    color: #6b7280;
                }}

                .card-value {{
                    font-size: 25px;
                    font-weight: bold;
                    margin-top: 8px;
                }}

                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 15px;
                }}

                th, td {{
                    border: 1px solid #e5e7eb;
                    padding: 10px;
                    text-align: left;
                }}

                th {{
                    background-color: #f3f4f6;
                }}

                li {{
                    margin-bottom: 6px;
                }}

                .footer {{
                    margin-top: 40px;
                    padding-top: 15px;
                    border-top: 1px solid #e5e7eb;
                    color: #6b7280;
                    font-size: 13px;
                }}

            </style>

        </head>

        <body>

            <div class="container">

                <h1>📊 InsightIQ</h1>

                <div class="subtitle">
                    AI-Powered Data Analytics Platform
                </div>

                <h2>📊 Dataset Overview</h2>

                <div class="summary">

                    <div class="card">

                        <div class="card-title">
                            Total Rows
                        </div>

                        <div class="card-value">
                            {df.shape[0]:,}
                        </div>

                    </div>

                    <div class="card">

                        <div class="card-title">
                            Total Columns
                        </div>

                        <div class="card-value">
                            {df.shape[1]}
                        </div>

                    </div>

                </div>

                <h2>📋 Column Names</h2>

                <ul>
                    {column_html}
                </ul>

                <h2>❗ Missing Values</h2>

                <table>

                    <tr>
                        <th>Column</th>
                        <th>Missing Values</th>
                    </tr>

                    {missing_html}

                </table>

                <h2>🔢 Numerical Columns</h2>

                <ul>
                    {numeric_html}
                </ul>

                <h2>🏷️ Categorical Columns</h2>

                <ul>
                    {categorical_html}
                </ul>

                <h2>🔁 Duplicate Rows</h2>

                <p>
                    {df.duplicated().sum()}
                    duplicate rows found in the cleaned dataset.
                </p>

                <div class="footer">

                    Generated by InsightIQ

                </div>

            </div>

        </body>

        </html>
        """

        # -------------------------------------------------
        # REPORT DOWNLOAD
        # -------------------------------------------------

        st.download_button(
            label="⬇️ Download Analysis Report",
            data=report_html,
            file_name="insightiq_analysis_report.html",
            mime="text/html"
        )

        show_success(
            "✅ Reports are ready for download."
        )

    else:

        st.info(
            "Please upload a dataset first."
        )


# =========================================================
# SETTINGS
# =========================================================
elif selected == "⚙️ Settings":

    st.title("⚙️ Settings")

    st.write(
        "Customize your InsightIQ experience."
    )

    # -------------------------------------------------
    # THEME SELECTION
    # -------------------------------------------------

    st.write("## 🎨 Theme Selection")

    if "theme" not in st.session_state:

        st.session_state.theme = "Light"

    theme = st.radio(
        "Choose your preferred theme:",
        ["Light", "Dark"],
        horizontal=True,
        index=(
            0
            if st.session_state.theme == "Light"
            else 1
        )
    )

    st.session_state.theme = theme

    # Theme styling is applied globally at the top of the application.
    st.write(
        f"**Selected Theme:** {theme}"
    )

    st.divider()

    # -------------------------------------------------
    # TABLE DISPLAY
    # -------------------------------------------------

    st.write("## 📋 Table Display")

    table_rows = st.selectbox(
        "Number of rows to display:",
        [5, 10, 20, 50, 100, "All"],
        index=[
            5,
            10,
            20,
            50,
            100,
            "All"
        ].index(
            st.session_state.table_rows
        )
    )

    st.session_state.table_rows = table_rows

    st.info(
        f"📋 Tables will display **{table_rows} rows**."
    )

    st.divider()

    # -------------------------------------------------
    # NOTIFICATIONS
    # -------------------------------------------------

    st.write("## 🔔 Notifications")

    notifications = st.toggle(
        "Show success notifications",
        value=st.session_state.notifications
    )

    st.session_state.notifications = notifications

    if notifications:
        st.info("Success notifications are enabled.")
    else:
        st.info("Success notifications are disabled.")

    st.divider()

    # -------------------------------------------------
    # ABOUT INSIGHTIQ
    # -------------------------------------------------

    st.write("## ℹ️ About InsightIQ")

    with st.expander(
        "About the Project",
        expanded=False
    ):

        st.write(
            """
            **InsightIQ** is an AI-Powered Data Analytics Platform
            designed to automatically analyze uploaded datasets.
            """
        )

        st.write("### 🛠️ Technology Stack")

        st.markdown(
            """
            - 🐍 Python
            - 🐼 Pandas
            - 🎈 Streamlit
            - 📊 Data Analysis
            - 📈 Data Visualization
            - 🤖 Gemini AI
            """
        )

    st.divider()

    # -------------------------------------------------
    # HELP
    # -------------------------------------------------

    st.write("## ❓ Help")

    with st.expander(
        "How to use InsightIQ"
    ):

        st.write(
            "### 1. 📂 Upload Dataset"
        )

        st.write(
            "Upload your CSV dataset from the Upload Dataset section."
        )

        st.write(
            "### 2. 📊 Dashboard"
        )

        st.write(
            "View dataset KPIs and visualizations."
        )

        st.write(
            "### 3. 🤖 AI Insights"
        )

        st.write(
            "View automatically generated insights from your cleaned dataset."
        )

        st.write(
            "### 4. 📄 Reports"
        )

        st.write(
            "Download the cleaned dataset and analysis report."
        )

        st.write(
            "### 5. ⚙️ Settings"
        )

        st.write(
            "Customize your application preferences."
        )