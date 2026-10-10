
import base64
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from redteam.core.session import SessionLocal
from redteam.models.attack import Attack
from redteam.models.target import Target
from redteam.reporting.security_summary import SecuritySummaryService
from redteam.repositories.attack_result import AttackResultRepository

PROJECT_ROOT = Path(__file__).resolve().parents[3]

REGRESSION_COMPARISON_PATH = Path(
    os.environ.get(
        "REGRESSION_COMPARISON_PATH",
        str(PROJECT_ROOT / "reports" / "regression-comparison.json"),
    )
)


st.set_page_config(
    page_title="AI Red Teaming Dashboard",
    page_icon="🛡️",
    layout="wide",
)

THEME_PATH = Path(__file__).with_name("theme.css")
BACKGROUND_PATH = PROJECT_ROOT / "assets" / "hacker-background.png"


def apply_hacker_theme() -> None:
    if not THEME_PATH.exists():
        return

    css = THEME_PATH.read_text(encoding="utf-8")

    if BACKGROUND_PATH.exists():
        encoded = base64.b64encode(
            BACKGROUND_PATH.read_bytes()
        ).decode("ascii")

        css += f"""
        [data-testid="stAppViewContainer"] {{
            background-image:
                linear-gradient(
                    rgba(5, 5, 8, 0.78),
                    rgba(5, 5, 8, 0.94)
                ),
                url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center top;
            background-attachment: fixed;
        }}
        """

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


apply_hacker_theme()

ANIMATION_PATH = Path(__file__).with_name("animation.html")

if ANIMATION_PATH.exists():
    components.html(
        ANIMATION_PATH.read_text(encoding="utf-8"),
        height=1,
        scrolling=False,
    )

st.title("🛡️ AI Red Teaming Dashboard")
st.caption(
    "Authorized AI security testing, execution monitoring, "
    "and security regression analysis."
)


# -------------------------------------------------------------------
# Sidebar controls
# -------------------------------------------------------------------

st.sidebar.header("Dashboard controls")

if st.sidebar.button("Refresh dashboard", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

recent_limit = st.sidebar.selectbox(
    "Recent executions to display",
    options=[10, 25, 50, 100],
    index=1,
)


# -------------------------------------------------------------------
# Load data from PostgreSQL
# -------------------------------------------------------------------

@st.cache_data(ttl=15)
def load_dashboard_data(limit: int) -> dict[str, Any]:
    """Read dashboard metrics and recent results from PostgreSQL."""
    with SessionLocal() as db:
        security_summary = SecuritySummaryService(db).build_summary()

        recent_results = AttackResultRepository(db).list_recent(
            limit=limit
        )

        attack_ids = {result.attack_id for result in recent_results}
        target_ids = {result.target_id for result in recent_results}

        attacks = {}
        targets = {}

        if attack_ids:
            attack_rows = db.scalars(
                select(Attack).where(Attack.id.in_(attack_ids))
            ).all()
            attacks = {attack.id: attack for attack in attack_rows}

        if target_ids:
            target_rows = db.scalars(
                select(Target).where(Target.id.in_(target_ids))
            ).all()
            targets = {target.id: target for target in target_rows}

        result_rows = []

        for result in recent_results:
            attack = attacks.get(result.attack_id)
            target = targets.get(result.target_id)

            result_rows.append(
                {
                    "Executed at": result.executed_at,
                    "Attack": attack.name if attack else "Unknown",
                    "Category": (
                        attack.category if attack else "Unknown"
                    ),
                    "Target": target.name if target else "Unknown",
                    "Execution status": result.execution_status,
                    "Attack succeeded": result.attack_succeeded,
                    "Severity": result.severity or "Unknown",
                    "Confidence": result.confidence,
                    "Model": result.model or "Unknown",
                    "Latency (ms)": result.latency_ms,
                }
            )

        return {
            "summary": security_summary,
            "recent_results": result_rows,
        }


# -------------------------------------------------------------------
# Load data and handle database errors
# -------------------------------------------------------------------

try:
    dashboard_data = load_dashboard_data(recent_limit)
except SQLAlchemyError as exc:
    st.error(
        "Could not load dashboard data from PostgreSQL. "
        "Check your database configuration and connection."
    )
    with st.expander("Technical details"):
        st.exception(exc)
    st.stop()


# -------------------------------------------------------------------
# Execution overview
# -------------------------------------------------------------------

summary = dashboard_data["summary"]["summary"]

st.header("Execution overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total executions",
    summary["total_executions"],
)
col2.metric(
    "Execution successes",
    summary["execution_successes"],
)
col3.metric(
    "Execution failures",
    summary["execution_failures"],
)
col4.metric(
    "Successful attacks",
    summary["successful_attacks"],
)

col5, col6, col7 = st.columns(3)

col5.metric(
    "Failed attacks",
    summary["failed_attacks"],
)
col6.metric(
    "Unscored results",
    summary["unscored_results"],
)

attack_success_rate = summary.get("attack_success_rate")

col7.metric(
    "Attack success rate",
    (
        f"{attack_success_rate:.1%}"
        if attack_success_rate is not None
        else "N/A"
    ),
)

st.caption(
    "Execution success means the test ran successfully. "
    "Attack success means the evaluator judged the attack successful. "
    "Attack success rate uses only scored executions."
)


# -------------------------------------------------------------------
# Results by category
# -------------------------------------------------------------------

st.header("Results by attack category")

category_rows = dashboard_data["summary"]["by_category"]
category_df = pd.DataFrame(category_rows)

if not category_df.empty:
    chart_df = category_df.set_index("category")[
        ["total", "succeeded"]
    ]

    st.bar_chart(chart_df)

    display_category_df = category_df.copy()
    display_category_df["success_rate"] = (
        display_category_df["success_rate"] * 100
    )

    st.dataframe(
        display_category_df.rename(
            columns={
                "category": "Category",
                "total": "Successful executions",
                "succeeded": "Successful attacks",
                "success_rate": "Attack success rate (%)",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info(
        "No successful executions are available for category analysis."
    )


# -------------------------------------------------------------------
# Recent executions
# -------------------------------------------------------------------

st.header("Recent executions")

results_df = pd.DataFrame(dashboard_data["recent_results"])

if results_df.empty:
    st.info("No executions have been recorded yet.")
else:
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    categories = sorted(
        results_df["Category"].dropna().unique().tolist()
    )
    targets = sorted(
        results_df["Target"].dropna().unique().tolist()
    )
    statuses = sorted(
        results_df["Execution status"].dropna().unique().tolist()
    )

    with filter_col1:
        selected_categories = st.multiselect(
            "Filter by category",
            options=categories,
            default=categories,
        )

    with filter_col2:
        selected_targets = st.multiselect(
            "Filter by target",
            options=targets,
            default=targets,
        )

    with filter_col3:
        selected_statuses = st.multiselect(
            "Filter by execution status",
            options=statuses,
            default=statuses,
        )

    filtered_df = results_df[
        results_df["Category"].isin(selected_categories)
        & results_df["Target"].isin(selected_targets)
        & results_df["Execution status"].isin(selected_statuses)
    ]

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        f"Showing {len(filtered_df)} of {len(results_df)} recent executions."
    )


# -------------------------------------------------------------------
# Security regression comparison
# -------------------------------------------------------------------

st.divider()
st.header("Security Regression Analysis")

if not REGRESSION_COMPARISON_PATH.exists():
    st.warning(
        "Regression comparison report was not found. "
        "Generate a comparison report to display regression metrics."
    )
else:
    try:
        comparison = json.loads(
            REGRESSION_COMPARISON_PATH.read_text(encoding="utf-8")
        )

        comparison_summary = comparison["summary"]
        regressions = comparison["regressions"]
        improvements = comparison["improvements"]
        unchanged = comparison["unchanged"]
        new_cases = comparison["new_cases"]
        removed_cases = comparison["removed_cases"]

        required_summary_keys = {
            "regressions",
            "improvements",
            "unchanged",
            "new_cases",
            "removed_cases",
        }

        if not required_summary_keys.issubset(comparison_summary):
            raise ValueError(
                "Regression summary is missing required fields."
            )

        regression_count = comparison_summary["regressions"]

        if regression_count > 0:
            st.error(
                f"{regression_count} regression(s) detected. "
                "Review the affected cases."
            )
        else:
            st.success(
                "No regressions were recorded in this comparison."
            )

        reg_col1, reg_col2, reg_col3 = st.columns(3)

        reg_col1.metric(
            "Regressions",
            comparison_summary["regressions"],
        )
        reg_col2.metric(
            "Improvements",
            comparison_summary["improvements"],
        )
        reg_col3.metric(
            "Unchanged",
            comparison_summary["unchanged"],
        )

        reg_col4, reg_col5 = st.columns(2)

        reg_col4.metric(
            "New cases",
            comparison_summary["new_cases"],
        )
        reg_col5.metric(
            "Removed cases",
            comparison_summary["removed_cases"],
        )

        def show_cases(title: str, cases: list[str]) -> None:
            with st.expander(f"{title} ({len(cases)})"):
                if cases:
                    st.dataframe(
                        [{"Test case": case} for case in cases],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.write("No cases in this group.")

        show_cases("Regressions", regressions)
        show_cases("Improvements", improvements)
        show_cases("Unchanged cases", unchanged)
        show_cases("New cases", new_cases)
        show_cases("Removed cases", removed_cases)

        st.caption(
            f"Previous report: "
            f"{comparison.get('previous_report', 'Unknown')}"
        )
        st.caption(
            f"Current report: "
            f"{comparison.get('current_report', 'Unknown')}"
        )

    except (
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        st.error(
            "The regression comparison report could not be read. "
            "Check its JSON structure."
        )
        with st.expander("Technical details"):
            st.exception(exc)


# -------------------------------------------------------------------
# Footer
# -------------------------------------------------------------------

st.divider()
st.caption(
    "AI Red Teaming Agent | "
    f"Last rendered: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}"
)
