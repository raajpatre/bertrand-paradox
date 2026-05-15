import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Bertrand's Paradox Simulator",
    page_icon="⭕",
    layout="wide",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Dark background throughout */
    .stApp { background-color: #0d0d0d; color: white; }
    [data-testid="stSidebar"] { background-color: #141414; border-right: 1px solid #2a2a2a; }

    /* Header */
    .main-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 900;
        color: white;
        letter-spacing: 2px;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    .main-subtitle {
        text-align: center;
        font-size: 1rem;
        color: #888;
        font-style: italic;
        margin-top: 4px;
        margin-bottom: 24px;
    }

    /* Result cards */
    .result-card {
        background: #1a1a1a;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 6px 0;
        border-left: 4px solid;
    }
    .card-label { font-size: 0.78rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }
    .card-value { font-size: 1.7rem; font-weight: 800; }
    .card-sub   { font-size: 0.82rem; color: #aaa; margin-top: 2px; }

    /* Method description box */
    .method-box {
        background: #1a1a1a;
        border-radius: 10px;
        padding: 14px 18px;
        border: 1px solid #2a2a2a;
        margin-bottom: 10px;
    }

    /* Sidebar labels */
    .stSlider label, .stRadio label { color: #ccc !important; font-size: 0.9rem !important; }
    
    /* Hide default streamlit footer */
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
RADIUS      = 1.0
SIDE_LENGTH = np.sqrt(3) * RADIUS   # ≈ 1.732

METHOD_INFO = {
    "Random Endpoints": {
        "color":  "#FF6B6B",
        "theory": 1/3,
        "desc":   "Pick 2 random points on the circumference → connect them.",
        "why":    "P = 1/3  —  The 2nd point must land in a specific 1/3 arc.",
        "emoji":  "🔴",
    },
    "Random Radius": {
        "color":  "#4ECDC4",
        "theory": 1/2,
        "desc":   "Pick a random radius direction, then a random distance along it → draw perpendicular chord.",
        "why":    "P = 1/2  —  Only the inner half of the radius gives a long chord.",
        "emoji":  "🟢",
    },
    "Random Midpoint": {
        "color":  "#FFE66D",
        "theory": 1/4,
        "desc":   "Pick a random point inside the circle → it becomes the chord's midpoint.",
        "why":    "P = 1/4  —  Only 1/4 of the disk area gives a long chord.",
        "emoji":  "🟡",
    },
}

# ─────────────────────────────────────────────
# CHORD GENERATION
# ─────────────────────────────────────────────
def method_endpoints(n, rng):
    t1 = rng.uniform(0, 2*np.pi, n)
    t2 = rng.uniform(0, 2*np.pi, n)
    x1, y1 = np.cos(t1), np.sin(t1)
    x2, y2 = np.cos(t2), np.sin(t2)
    return x1, y1, x2, y2, np.sqrt((x2-x1)**2 + (y2-y1)**2)

def method_radius(n, rng):
    t = rng.uniform(0, 2*np.pi, n)
    d = rng.uniform(0, RADIUS, n)
    half = np.sqrt(RADIUS**2 - d**2)
    mx, my = d*np.cos(t), d*np.sin(t)
    px, py = -np.sin(t), np.cos(t)
    return mx+half*px, my+half*py, mx-half*px, my-half*py, 2*half

def method_midpoint(n, rng):
    pts = []
    while len(pts) < n:
        x = rng.uniform(-RADIUS, RADIUS, n*2)
        y = rng.uniform(-RADIUS, RADIUS, n*2)
        mask = x**2 + y**2 <= RADIUS**2
        pts.extend(zip(x[mask], y[mask]))
    pts = np.array(pts[:n])
    mx, my = pts[:,0], pts[:,1]
    d2   = mx**2 + my**2
    half = np.sqrt(np.maximum(RADIUS**2 - d2, 0))
    r    = np.sqrt(d2)
    safe = r > 1e-10
    px   = np.where(safe, -my/np.where(safe, r, 1), 1.0)
    py   = np.where(safe,  mx/np.where(safe, r, 1), 0.0)
    return mx+half*px, my+half*py, mx-half*px, my-half*py, 2*half

METHODS = {
    "Random Endpoints": method_endpoints,
    "Random Radius":    method_radius,
    "Random Midpoint":  method_midpoint,
}

# ─────────────────────────────────────────────
# SIDEBAR CONTROLS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    st.markdown("---")

    method_name = st.radio(
        "Select Method",
        list(METHODS.keys()),
        index=0,
    )

    st.markdown("---")

    n_chords = st.slider("Number of Chords", 10, 2000, 100, step=10)
    seed     = st.slider("Random Seed", 0, 100, 42, step=1)

    regenerate = st.button("⟳  Regenerate", use_container_width=True, type="primary")
    if regenerate:
        seed = (seed + 1) % 101
        st.rerun()

    st.markdown("---")

    info = METHOD_INFO[method_name]
    st.markdown(f"""
    <div class="method-box">
        <div style="font-size:1rem; font-weight:700; color:{info['color']}; margin-bottom:6px;">
            {info['emoji']} {method_name}
        </div>
        <div style="font-size:0.85rem; color:#ccc; margin-bottom:8px;">{info['desc']}</div>
        <div style="font-size:0.85rem; color:{info['color']}; font-weight:600;">{info['why']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="color:#555; font-size:0.75rem; text-align:center; margin-top:20px;">
        Circle radius r = 1<br>
        Threshold = √3 ≈ 1.732<br>
        (side of inscribed equilateral triangle)
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GENERATE DATA
# ─────────────────────────────────────────────
rng = np.random.default_rng(seed)
x1, y1, x2, y2, lengths = METHODS[method_name](n_chords, rng)
favorable  = lengths > SIDE_LENGTH
prob       = favorable.mean()
theory     = METHOD_INFO[method_name]["theory"]
color      = METHOD_INFO[method_name]["color"]
n_fav      = favorable.sum()
n_unfav    = (~favorable).sum()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="main-title">BERTRAND\'S PARADOX — INTERACTIVE SIMULATOR</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Same question · Three different methods · Three different answers</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# RESULT CARDS  (top row)
# ─────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)

def card(col, label, value, sub, color):
    col.markdown(f"""
    <div class="result-card" style="border-left-color:{color}">
        <div class="card-label">{label}</div>
        <div class="card-value" style="color:{color}">{value}</div>
        <div class="card-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

card(c1, "Method",        method_name.split()[1],  method_name,              color)
card(c2, "Total Chords",  f"{n_chords:,}",          "simulated",              "#888")
card(c3, "Favorable",     f"{n_fav:,}",             f"{100*prob:.1f}%  long", color)
card(c4, "Simulated P",   f"{prob:.4f}",            f"theory = {theory:.4f}", color)
card(c5, "|Error|",       f"{abs(prob-theory):.4f}", "vs theoretical",        "#888" if abs(prob-theory) < 0.05 else "#FF6B6B")

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PLOTS
# ─────────────────────────────────────────────
col_left, col_right = st.columns([1, 1])

# ══════════════════
# LEFT: Circle Plot
# ══════════════════
with col_left:
    theta = np.linspace(0, 2*np.pi, 300)

    fig_circle = go.Figure()

    # Circle boundary
    fig_circle.add_trace(go.Scatter(
        x=np.cos(theta), y=np.sin(theta),
        mode="lines", line=dict(color="white", width=2.5),
        showlegend=False, hoverinfo="skip"
    ))

    # Inscribed triangle
    tri_angles = np.array([np.pi/2, np.pi/2 + 2*np.pi/3, np.pi/2 + 4*np.pi/3, np.pi/2])
    fig_circle.add_trace(go.Scatter(
        x=np.cos(tri_angles), y=np.sin(tri_angles),
        mode="lines",
        line=dict(color="#666", width=1.5, dash="dash"),
        fill="toself", fillcolor="rgba(100,100,100,0.1)",
        name="Inscribed Triangle  (side = √3)",
        hoverinfo="skip"
    ))

    # Limit display to 150 chords
    n_display   = min(n_chords, 150)
    fav_idx     = np.where(favorable[:n_display])[0]
    unfav_idx   = np.where(~favorable[:n_display])[0]

    # Unfavorable chords (dark, thin)
    for i in unfav_idx:
        fig_circle.add_trace(go.Scatter(
            x=[x1[i], x2[i], None], y=[y1[i], y2[i], None],
            mode="lines", line=dict(color="#2a2a2a", width=0.8),
            showlegend=False, hoverinfo="skip"
        ))

    # Favorable chords — batch into one trace using None separators
    fx, fy = [], []
    for i in fav_idx:
        fx += [x1[i], x2[i], None]
        fy += [y1[i], y2[i], None]
    if fx:
        fig_circle.add_trace(go.Scatter(
            x=fx, y=fy,
            mode="lines",
            line=dict(color=color, width=1.5),
            name=f"Long chord  (> √3)",
            hoverinfo="skip"
        ))

    # One dummy trace for the unfavorable legend entry
    fig_circle.add_trace(go.Scatter(
        x=[None], y=[None],
        mode="lines", line=dict(color="#444", width=2),
        name="Short chord  (< √3)"
    ))

    fig_circle.update_layout(
        title=dict(
            text=f"<b>{method_name.upper()}</b>",
            font=dict(color=color, size=16),
            x=0.5
        ),
        paper_bgcolor="#0d0d0d",
        plot_bgcolor="#0d0d0d",
        height=480,
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(range=[-1.45, 1.45], showgrid=False, zeroline=False,
                   showticklabels=False, scaleanchor="y"),
        yaxis=dict(range=[-1.45, 1.45], showgrid=False, zeroline=False,
                   showticklabels=False),
        legend=dict(
            x=0.01, y=0.01,
            bgcolor="rgba(20,20,20,0.9)",
            bordercolor="#444", borderwidth=1,
            font=dict(color="white", size=11)
        ),
        showlegend=True,
    )

    st.plotly_chart(fig_circle, use_container_width=True)

# ═══════════════════════════════
# RIGHT: Convergence + Histogram
# ═══════════════════════════════
with col_right:

    # Convergence
    running_prob = np.cumsum(favorable) / np.arange(1, n_chords+1)
    trials       = np.arange(1, n_chords+1)

    fig_conv = go.Figure()

    # Shaded band around theory
    fig_conv.add_trace(go.Scatter(
        x=np.concatenate([trials, trials[::-1]]),
        y=np.concatenate([np.full(n_chords, theory+0.05),
                          np.full(n_chords, theory-0.05)[::-1]]),
        fill="toself", fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2],16) for i in (0,2,4)) + (0.12,)}",
        line=dict(width=0), showlegend=False, hoverinfo="skip"
    ))

    fig_conv.add_trace(go.Scatter(
        x=trials, y=running_prob,
        mode="lines", line=dict(color=color, width=2),
        name="Simulated"
    ))

    fig_conv.add_hline(
        y=theory, line_dash="dash", line_color="white", line_width=1.5,
        annotation_text=f"Theory = {theory:.4f}",
        annotation_font_color="white", annotation_font_size=11
    )

    fig_conv.update_layout(
        title=dict(text="<b>Probability Convergence</b>",
                   font=dict(color="white", size=14), x=0.5),
        paper_bgcolor="#0d0d0d", plot_bgcolor="#0d0d0d",
        height=220, margin=dict(l=40, r=20, t=40, b=30),
        xaxis=dict(title="Number of Trials", color="#999",
                   gridcolor="#1a1a1a", showline=True, linecolor="#444"),
        yaxis=dict(title="P(length > √3)", color="#999",
                   gridcolor="#1a1a1a", showline=True, linecolor="#444"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="white", size=10)),
        font=dict(color="#999"),
    )

    st.plotly_chart(fig_conv, use_container_width=True)

    # Histogram
    fig_hist = go.Figure()

    fig_hist.add_trace(go.Histogram(
        x=lengths,
        nbinsx=50,
        marker_color=color, opacity=0.85,
        histnorm="probability density",
        name="Chord lengths",
    ))

    fig_hist.add_vline(
        x=SIDE_LENGTH, line_dash="dash", line_color="white", line_width=2,
        annotation_text=f"√3 ≈ {SIDE_LENGTH:.3f}",
        annotation_font_color="white", annotation_font_size=11,
        annotation_position="top left"
    )

    # Shade favorable region
    fig_hist.add_vrect(
        x0=SIDE_LENGTH, x1=2.0,
        fillcolor=color, opacity=0.08,
        layer="below", line_width=0,
    )

    fig_hist.update_layout(
        title=dict(text="<b>Chord Length Distribution</b>",
                   font=dict(color="white", size=14), x=0.5),
        paper_bgcolor="#0d0d0d", plot_bgcolor="#0d0d0d",
        height=220, margin=dict(l=40, r=20, t=40, b=30),
        xaxis=dict(title="Chord Length", color="#999",
                   gridcolor="#1a1a1a", showline=True, linecolor="#444",
                   range=[0, 2.05]),
        yaxis=dict(title="Density", color="#999",
                   gridcolor="#1a1a1a", showline=True, linecolor="#444"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="white", size=10)),
        showlegend=False,
        font=dict(color="#999"),
    )

    st.plotly_chart(fig_hist, use_container_width=True)

# ─────────────────────────────────────────────
# COMPARISON TABLE (all 3 methods at once)
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📊 All Three Methods — Side by Side")

rng2 = np.random.default_rng(seed)
comparison_data = {}
for mname, mfunc in METHODS.items():
    rng2 = np.random.default_rng(seed)
    _, _, _, _, lens = mfunc(n_chords, rng2)
    fav  = lens > SIDE_LENGTH
    comparison_data[mname] = {
        "color":    METHOD_INFO[mname]["color"],
        "prob":     fav.mean(),
        "theory":   METHOD_INFO[mname]["theory"],
        "error":    abs(fav.mean() - METHOD_INFO[mname]["theory"]),
    }

# Bar chart comparing all 3
fig_bar = go.Figure()

mnames  = list(comparison_data.keys())
sim_p   = [comparison_data[m]["prob"]   for m in mnames]
theo_p  = [comparison_data[m]["theory"] for m in mnames]
colors  = [comparison_data[m]["color"]  for m in mnames]

fig_bar.add_trace(go.Bar(
    x=mnames, y=sim_p,
    name="Simulated",
    marker_color=colors,
    opacity=0.9,
    text=[f"{p:.4f}" for p in sim_p],
    textposition="outside",
    textfont=dict(color="white", size=12)
))

fig_bar.add_trace(go.Bar(
    x=mnames, y=theo_p,
    name="Theoretical",
    marker_color=colors,
    opacity=0.35,
    text=[f"{p:.4f}" for p in theo_p],
    textposition="outside",
    textfont=dict(color="#aaa", size=12)
))

# Add theory lines
for i, (m, p) in enumerate(zip(mnames, theo_p)):
    fig_bar.add_shape(type="line",
        x0=i-0.4, x1=i+0.4, y0=p, y1=p,
        line=dict(color="white", width=1.5, dash="dot"))

fig_bar.update_layout(
    paper_bgcolor="#0d0d0d", plot_bgcolor="#0d0d0d",
    height=320, barmode="group",
    margin=dict(l=20, r=20, t=20, b=20),
    xaxis=dict(color="#ccc", gridcolor="#1a1a1a", tickfont=dict(size=13)),
    yaxis=dict(title="Probability", color="#999", gridcolor="#1a1a1a",
               range=[0, 0.72]),
    legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
    font=dict(color="#999"),
)

st.plotly_chart(fig_bar, use_container_width=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#444; font-size:0.8rem; margin-top:30px; padding-bottom:20px;">
    Bertrand's Paradox (1889) · PnS Project — Group 8 · SVyasa University<br>
    Circle r = 1 &nbsp;|&nbsp; Threshold = √3 ≈ 1.732 &nbsp;|&nbsp; Inscribed equilateral triangle side
</div>
""", unsafe_allow_html=True)
