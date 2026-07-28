from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Optional

import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000/calculate"
OPERATIONS = {
    "+": "add",
    "-": "subtract",
    "x": "multiply",
    "÷": "divide",
    "%": "percent",
}


st.set_page_config(page_title="Calculator", page_icon="🧮", layout="centered")


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --calc-shell: #22252d;
            --calc-shell-dark: #15171d;
            --display: #101217;
            --display-text: #f4f7fb;
            --key: #30343e;
            --key-hover: #3a3f4b;
            --operator: #f2a33a;
            --operator-hover: #ffb852;
            --function: #a9b0bc;
            --function-text: #111318;
            --equals: #ff9f2f;
            --equals-hover: #ffae46;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(255, 159, 47, 0.14), transparent 24rem),
                linear-gradient(135deg, #151922 0%, #07090d 100%);
        }

        .block-container {
            max-width: 430px;
            padding-top: 3rem;
            padding-bottom: 2rem;
        }

        div[data-testid="stMainBlockContainer"] {
            background: linear-gradient(145deg, #232832, #11151c);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 30px;
            box-shadow: 0 26px 70px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.08);
            margin-top: 1.25rem;
            padding-left: 1.35rem;
            padding-right: 1.35rem;
        }

        .calculator-shell {
            display: none;
        }

        .brand-row {
            align-items: center;
            color: #d8dee8;
            display: flex;
            font-size: 0.78rem;
            font-weight: 700;
            justify-content: space-between;
            letter-spacing: 0;
            margin: 0 auto 0.7rem;
            max-width: 380px;
            padding: 0 0.45rem;
        }

        .sensor {
            background: #f4f7fb;
            border-radius: 999px;
            height: 0.42rem;
            width: 2.8rem;
        }

        .display {
            background: #05070a;
            border: 1px solid rgba(255,255,255,0.16);
            border-radius: 18px;
            color: var(--display-text);
            box-shadow: 0 18px 40px rgba(0, 0, 0, 0.45);
            margin: 0 auto 1rem;
            max-width: 380px;
            min-height: 112px;
            overflow: hidden;
            padding: 1rem;
            text-align: right;
        }

        .expression {
            color: #ffffff;
            color: #ffffff;
            font-family: Consolas, "Courier New", monospace;
            font-size: 0.95rem;
            min-height: 1.35rem;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .screen-value {
            font-family: Consolas, "Courier New", monospace;
            font-size: 2.55rem;
            font-weight: 700;
            letter-spacing: 0;
            line-height: 1.18;
            margin-top: 0.55rem;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        div[data-testid="column"] {
            padding-left: 0.25rem;
            padding-right: 0.25rem;
        }

        div[data-testid="stHorizontalBlock"] {
            margin-left: auto;
            margin-right: auto;
            max-width: 380px;
        }

        .stButton > button {
            border: 1px solid rgba(255,255,255,0.82);
            border-radius: 18px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 7px 14px rgba(0,0,0,0.16);
            font-size: 1.35rem;
            font-weight: 700;
            height: 4.05rem;
            line-height: 1;
            transition: transform 120ms ease, filter 120ms ease, background 120ms ease;
            width: 100%;
        }

        .stButton > button:hover {
            filter: brightness(1.06);
            transform: translateY(-1px);
        }

        .stButton > button:active {
            transform: translateY(1px);
        }

        .key-digit > button, .key-decimal > button {
            background: var(--key);
            color: #f6f7fb;
        }

        .key-digit > button:hover, .key-decimal > button:hover {
            background: var(--key-hover);
            color: #ffffff;
        }

        .key-function > button {
            background: var(--function);
            border-color: rgba(255,255,255,0.72);
            color: var(--function-text);
        }

        .key-operator > button {
            background: var(--operator);
            border-color: rgba(255,194,106,0.86);
            color: #19140c;
        }

        .key-operator > button:hover {
            background: var(--operator-hover);
            color: #19140c;
        }

        .stButton button[kind="primary"],
        .stButton button[data-testid="stBaseButton-primary"] {
            background: var(--equals) !important;
            border: 0 !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.2), 0 6px 0 #c7741c, 0 10px 16px rgba(0,0,0,0.18) !important;
            color: #34343a !important;
            font-size: 1.65rem !important;
        }

        .stButton button[kind="primary"]:hover,
        .stButton button[data-testid="stBaseButton-primary"]:hover {
            background: var(--equals-hover) !important;
            color: #34343a !important;
        }

        .status-line {
            color: #596273;
            font-size: 0.82rem;
            margin-top: 0.8rem;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initial_state() -> None:
    defaults = {
        "display": "0",
        "left": None,
        "operator": None,
        "waiting_for_next": False,
        "expression": "",
        "error": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def parse_display() -> Decimal:
    try:
        return Decimal(st.session_state.display)
    except InvalidOperation as exc:
        raise ValueError("Display value is not a valid number") from exc


def set_display(value: str) -> None:
    st.session_state.display = value[:18]


def clear_all() -> None:
    st.session_state.display = "0"
    st.session_state.left = None
    st.session_state.operator = None
    st.session_state.waiting_for_next = False
    st.session_state.expression = ""
    st.session_state.error = ""


def input_digit(digit: str) -> None:
    st.session_state.error = ""
    if st.session_state.waiting_for_next or st.session_state.display == "0":
        st.session_state.display = digit
        st.session_state.waiting_for_next = False
        return

    if len(st.session_state.display.replace("-", "").replace(".", "")) < 12:
        st.session_state.display += digit


def input_decimal() -> None:
    st.session_state.error = ""
    if st.session_state.waiting_for_next:
        st.session_state.display = "0."
        st.session_state.waiting_for_next = False
        return

    if "." not in st.session_state.display:
        st.session_state.display += "."


def toggle_sign() -> None:
    st.session_state.error = ""
    if st.session_state.display == "0":
        return
    if st.session_state.display.startswith("-"):
        st.session_state.display = st.session_state.display[1:]
    else:
        st.session_state.display = f"-{st.session_state.display}"


def backspace() -> None:
    st.session_state.error = ""
    if st.session_state.waiting_for_next:
        return
    text = st.session_state.display[:-1]
    st.session_state.display = text if text and text != "-" else "0"


def call_api(left: Decimal, right: Decimal, operator: str) -> str:
    response = requests.post(
        API_URL,
        json={
            "left": str(left),
            "right": str(right),
            "operation": OPERATIONS[operator],
        },
        timeout=3,
    )
    if response.status_code >= 400:
        detail = response.json().get("detail", "Calculation failed")
        raise ValueError(detail)
    return response.json()["result"]


def calculate_pending(next_operator: Optional[str] = None) -> None:
    if st.session_state.left is None or st.session_state.operator is None:
        st.session_state.left = str(parse_display())
        st.session_state.operator = next_operator
        st.session_state.expression = (
            f"{st.session_state.left} {next_operator}" if next_operator else ""
        )
        st.session_state.waiting_for_next = True
        return

    left = Decimal(st.session_state.left)
    right = parse_display()
    operator = st.session_state.operator
    result = call_api(left, right, operator)

    st.session_state.display = result
    st.session_state.left = result
    st.session_state.operator = next_operator
    st.session_state.waiting_for_next = True
    st.session_state.expression = (
        f"{result} {next_operator}" if next_operator else f"{left} {operator} {right} ="
    )


def choose_operator(operator: str) -> None:
    st.session_state.error = ""
    try:
        if st.session_state.operator and not st.session_state.waiting_for_next:
            calculate_pending(operator)
        else:
            st.session_state.left = str(parse_display())
            st.session_state.operator = operator
            st.session_state.expression = f"{st.session_state.left} {operator}"
            st.session_state.waiting_for_next = True
    except (requests.RequestException, ValueError) as exc:
        st.session_state.error = str(exc)


def equals() -> None:
    st.session_state.error = ""
    try:
        calculate_pending(None)
        st.session_state.left = None
        st.session_state.operator = None
    except (requests.RequestException, ValueError) as exc:
        st.session_state.error = str(exc)


def percent() -> None:
    st.session_state.error = ""
    try:
        value = parse_display()
        base = Decimal(st.session_state.left) if st.session_state.left else Decimal("1")
        result = call_api(base, value, "%")
        set_display(result)
    except (requests.RequestException, ValueError) as exc:
        st.session_state.error = str(exc)


def button(label: str, kind: str, callback, args: tuple = ()) -> None:
    st.markdown(f'<div class="key-{kind}">', unsafe_allow_html=True)
    button_type = "primary" if kind == "equals" else "secondary"
    st.button(
        label,
        type=button_type,
        use_container_width=True,
        on_click=callback,
        args=args,
    )
    st.markdown("</div>", unsafe_allow_html=True)


inject_styles()
initial_state()

st.markdown('<span class="calculator-shell"></span>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="brand-row">
        <span>CALCULATOR</span>
        <span class="sensor"></span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    f"""
    <div class="display">
        <div class="expression">{st.session_state.expression or "&nbsp;"}</div>
        <div class="screen-value">{st.session_state.display}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

rows = [
    [("AC", "function", clear_all, ()), ("+/-", "function", toggle_sign, ()), ("%", "function", percent, ()), ("÷", "operator", choose_operator, ("÷",))],
    [("7", "digit", input_digit, ("7",)), ("8", "digit", input_digit, ("8",)), ("9", "digit", input_digit, ("9",)), ("x", "operator", choose_operator, ("x",))],
    [("4", "digit", input_digit, ("4",)), ("5", "digit", input_digit, ("5",)), ("6", "digit", input_digit, ("6",)), ("-", "operator", choose_operator, ("-",))],
    [("1", "digit", input_digit, ("1",)), ("2", "digit", input_digit, ("2",)), ("3", "digit", input_digit, ("3",)), ("+", "operator", choose_operator, ("+",))],
    [("⌫", "function", backspace, ()), ("0", "digit", input_digit, ("0",)), (".", "decimal", input_decimal, ()), ("=", "equals", equals, ())],
]

for row in rows:
    cols = st.columns(4)
    for col, spec in zip(cols, row):
        with col:
            button(*spec)

status = st.session_state.error or "Start FastAPI on port 8000 before using the keys."
st.markdown(f'<div class="status-line">{status}</div>', unsafe_allow_html=True)
