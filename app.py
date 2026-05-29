import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Bertrand's Paradox Simulator",
    page_icon="⭕",
    layout="wide",
)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
RADIUS      = 1.0
SIDE_LENGTH = np.sqrt(3) * RADIUS   # ≈ 1.732

METHOD_INFO = {
    "Random Endpoints": {
        "color":  "#FF5C5C",
        "theory": 1/3,
        "desc":   "Pick 2 random points on the circumference, connect them.",
        "why":    "P = 1/3 — the 2nd point must land in a specific 1/3 arc.",
    },
    "Random Radius": {
        "color":  "#4ECDC4",
        "theory": 1/2,
        "desc":   "Pick a random radius, a random point on it, draw the perpendicular chord.",
        "why":    "P = 1/2 — only the inner half of the radius gives a long chord.",
    },
    "Random Midpoint": {
        "color":  "#FFD93D",
        "theory": 1/4,
        "desc":   "Pick a random point inside the disk; it becomes the chord's midpoint.",
        "why":    "P = 1/4 — only 1/4 of the disk area gives a long chord.",
    },
}

# ─────────────────────────────────────────────
# CHORD GENERATION  (returns endpoints, midpoints, lengths)
# ─────────────────────────────────────────────
def method_endpoints(n, rng):
    t1 = rng.uniform(0, 2*np.pi, n)
    t2 = rng.uniform(0, 2*np.pi, n)
    x1, y1 = np.cos(t1), np.sin(t1)
    x2, y2 = np.cos(t2), np.sin(t2)
    mx, my = (x1+x2)/2, (y1+y2)/2
    return x1, y1, x2, y2, mx, my, np.sqrt((x2-x1)**2 + (y2-y1)**2)

def method_radius(n, rng):
    t = rng.uniform(0, 2*np.pi, n)
    d = rng.uniform(0, RADIUS, n)
    half = np.sqrt(RADIUS**2 - d**2)
    mx, my = d*np.cos(t), d*np.sin(t)
    px, py = -np.sin(t), np.cos(t)
    return (mx+half*px, my+half*py, mx-half*px, my-half*py,
            mx, my, 2*half)

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
    return (mx+half*px, my+half*py, mx-half*px, my-half*py,
            mx, my, 2*half)

METHODS = {
    "Random Endpoints": method_endpoints,
    "Random Radius":    method_radius,
    "Random Midpoint":  method_midpoint,
}

# ─────────────────────────────────────────────
# CIRCLE FIGURE BUILDER
# Wikipedia-style: thin chords, grey triangle, red=long blue=short
# ─────────────────────────────────────────────
def build_circle_figure(method_name, x1, y1, x2, y2, mx, my, favorable,
                         n_show, show_midpoints):
    color = METHOD_INFO[method_name]["color"]
    theta = np.linspace(0, 2*np.pi, 300)

    fig = go.Figure()

    # Circle boundary
    fig.add_trace(go.Scatter(
        x=np.cos(theta), y=np.sin(theta),
        mode="lines", line=dict(color="#cccccc", width=2),
        showlegend=False, hoverinfo="skip"))

    # Inscribed triangle (grey, like Wikipedia)
    tri = np.array([np.pi/2, np.pi/2+2*np.pi/3, np.pi/2+4*np.pi/3, np.pi/2])
    fig.add_trace(go.Scatter(
        x=np.cos(tri), y=np.sin(tri),
        mode="lines", line=dict(color="#888888", width=1.5),
        fill="toself", fillcolor="rgba(150,150,150,0.12)",
        showlegend=False, hoverinfo="skip"))

    # Split favorable / unfavorable up to n_show
    idx = np.arange(n_show)
    fav = idx[favorable[:n_show]]
    unf = idx[~favorable[:n_show]]

    # Short chords (blue) — thin
    bx, by = [], []
    for i in unf:
        bx += [x1[i], x2[i], None]; by += [y1[i], y2[i], None]
    if bx:
        fig.add_trace(go.Scatter(
            x=bx, y=by, mode="lines",
            line=dict(color="#5B8DEF", width=0.6),
            name="Short (< √3)", hoverinfo="skip"))

    # Long chords (red) — thin
    rx, ry = [], []
    for i in fav:
        rx += [x1[i], x2[i], None]; ry += [y1[i], y2[i], None]
    if rx:
        fig.add_trace(go.Scatter(
            x=rx, y=ry, mode="lines",
            line=dict(color="#FF5C5C", width=0.6),
            name="Long (> √3)", hoverinfo="skip"))

    # Optional midpoint cloud
    if show_midpoints:
        fig.add_trace(go.Scatter(
            x=mx[:n_show][favorable[:n_show]],
            y=my[:n_show][favorable[:n_show]],
            mode="markers",
            marker=dict(color="#FF5C5C", size=3, opacity=0.7),
            name="Long midpoint", hoverinfo="skip"))
        fig.add_trace(go.Scatter(
            x=mx[:n_show][~favorable[:n_show]],
            y=my[:n_show][~favorable[:n_show]],
            mode="markers",
            marker=dict(color="#5B8DEF", size=3, opacity=0.7),
            name="Short midpoint", hoverinfo="skip"))
        # r/2 reference circle
        fig.add_trace(go.Scatter(
            x=0.5*np.cos(theta), y=0.5*np.sin(theta),
            mode="lines", line=dict(color="#FFD93D", width=1, dash="dot"),
            name="r/2 boundary", hoverinfo="skip"))

    fig.update_layout(
        paper_bgcolor="#0d0d0d", plot_bgcolor="#0d0d0d",
        height=620,  # large — about half the page
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(range=[-1.15, 1.15], showgrid=False, zeroline=False,
                   showticklabels=False, scaleanchor="y"),
        yaxis=dict(range=[-1.15, 1.15], showgrid=False, zeroline=False,
                   showticklabels=False),
        legend=dict(x=0.5, y=-0.02, xanchor="center", orientation="h",
                    bgcolor="rgba(20,20,20,0.8)", bordercolor="#333",
                    borderwidth=1, font=dict(color="white", size=11)),
        showlegend=True)
    return fig

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    st.markdown("---")

    method_name = st.radio("Method", list(METHODS.keys()), index=0)
    n_chords    = st.slider("Number of Chords", 10, 1500, 300, step=10)
    seed        = st.slider("Random Seed", 0, 100, 42, step=1)

    st.markdown("---")
    st.markdown("#### ✨ Unique Features")
    animate        = st.checkbox("▶ Animate chords drawing in", value=False)
    anim_speed     = st.select_slider("Animation speed",
                        options=["Slow", "Medium", "Fast"], value="Medium")
    show_midpoints = st.checkbox("◉ Show chord midpoints", value=False,
                        help="Reveals WHY the methods differ — midpoint density")

    st.markdown("---")
    info = METHOD_INFO[method_name]
    st.markdown(f"**{method_name}**")
    st.caption(info["desc"])
    st.markdown(f"<span style='color:{info['color']};font-weight:600'>{info['why']}</span>",
                unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Circle r = 1 · Threshold √3 ≈ 1.732\n\nInscribed equilateral triangle side")

# ─────────────────────────────────────────────
# GENERATE DATA
# ─────────────────────────────────────────────
rng = np.random.default_rng(seed)
x1, y1, x2, y2, mx, my, lengths = METHODS[method_name](n_chords, rng)
favorable = lengths > SIDE_LENGTH
prob      = favorable.mean()
theory    = METHOD_INFO[method_name]["theory"]
color     = METHOD_INFO[method_name]["color"]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center;letter-spacing:2px;'>BERTRAND'S PARADOX</h1>"
    "<p style='text-align:center;color:#888;font-style:italic;margin-top:-10px;'>"
    "Same question · three definitions of random · three different answers</p>",
    unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN LAYOUT: big circle (left) | stats + animation (right)
# ─────────────────────────────────────────────
col_circle, col_side = st.columns([1.1, 0.9])

# Right side: live stats placeholders
with col_side:
    st.markdown(f"### {method_name}")
    stat_prob   = st.empty()
    stat_counts = st.empty()
    prog        = st.empty()

with col_circle:
    circle_slot = st.empty()

# ─────────────────────────────────────────────
# ANIMATION  vs  STATIC RENDER
# ─────────────────────────────────────────────
def render_stats(n_shown, fav_count):
    p = fav_count / n_shown if n_shown else 0
    stat_prob.markdown(
        f"<div style='font-size:3rem;font-weight:800;color:{color};'>"
        f"P = {p:.4f}</div>"
        f"<div style='color:#888;margin-top:-8px;'>theoretical = {theory:.4f} "
        f"&nbsp;|&nbsp; error = {abs(p-theory):.4f}</div>",
        unsafe_allow_html=True)
    stat_counts.markdown(
        f"**Chords drawn:** {n_shown:,}  \n"
        f"**Long (> √3):** {fav_count:,} ({100*p:.1f}%)  \n"
        f"**Short (< √3):** {n_shown-fav_count:,} ({100*(1-p):.1f}%)")

if animate:
    delays = {"Slow": 0.06, "Medium": 0.025, "Fast": 0.008}
    delay  = delays[anim_speed]
    # Draw in batches for smoothness (animate up to 300 frames max)
    n_anim = min(n_chords, 300)
    step   = max(1, n_anim // 60)   # ~60 frames
    cum_fav = np.cumsum(favorable)
    for k in range(step, n_anim + step, step):
        k = min(k, n_anim)
        fig = build_circle_figure(method_name, x1, y1, x2, y2, mx, my,
                                  favorable, k, show_midpoints)
        circle_slot.plotly_chart(fig, use_container_width=True,
                                  key=f"anim_{k}")
        render_stats(k, int(cum_fav[k-1]))
        prog.progress(k / n_anim)
        time.sleep(delay)
    prog.empty()
    # Final full render with all chords
    fig = build_circle_figure(method_name, x1, y1, x2, y2, mx, my,
                              favorable, min(n_chords, 300), show_midpoints)
    circle_slot.plotly_chart(fig, use_container_width=True, key="anim_final")
    render_stats(n_chords, int(favorable.sum()))
else:
    n_show = min(n_chords, 300)
    fig = build_circle_figure(method_name, x1, y1, x2, y2, mx, my,
                              favorable, n_show, show_midpoints)
    circle_slot.plotly_chart(fig, use_container_width=True, key="static")
    render_stats(n_chords, int(favorable.sum()))

# ─────────────────────────────────────────────
# LOWER ROW: convergence + histogram
# ─────────────────────────────────────────────
st.markdown("---")
c1, c2 = st.columns(2)

with c1:
    running = np.cumsum(favorable) / np.arange(1, n_chords+1)
    f = go.Figure()
    f.add_trace(go.Scatter(y=running, mode="lines",
                line=dict(color=color, width=2), name="Simulated"))
    f.add_hline(y=theory, line_dash="dash", line_color="white",
                annotation_text=f"Theory = {theory:.4f}",
                annotation_font_color="white")
    f.update_layout(
        title=dict(text="<b>Probability Convergence</b>",
                   font=dict(color="white", size=14), x=0.5),
        paper_bgcolor="#0d0d0d", plot_bgcolor="#0d0d0d", height=300,
        margin=dict(l=40, r=20, t=40, b=30),
        xaxis=dict(title="Trials", color="#999", gridcolor="#1a1a1a"),
        yaxis=dict(title="P(length > √3)", color="#999", gridcolor="#1a1a1a"),
        legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
        font=dict(color="#999"))
    st.plotly_chart(f, use_container_width=True, key="conv")

with c2:
    f = go.Figure()
    f.add_trace(go.Histogram(x=lengths, nbinsx=50, marker_color=color,
                opacity=0.85, histnorm="probability density"))
    f.add_vline(x=SIDE_LENGTH, line_dash="dash", line_color="white",
                annotation_text=f"√3 ≈ {SIDE_LENGTH:.3f}",
                annotation_font_color="white", annotation_position="top left")
    f.add_vrect(x0=SIDE_LENGTH, x1=2.0, fillcolor=color, opacity=0.08,
                layer="below", line_width=0)
    f.update_layout(
        title=dict(text="<b>Chord Length Distribution</b>",
                   font=dict(color="white", size=14), x=0.5),
        paper_bgcolor="#0d0d0d", plot_bgcolor="#0d0d0d", height=300,
        margin=dict(l=40, r=20, t=40, b=30),
        xaxis=dict(title="Chord Length", color="#999", gridcolor="#1a1a1a",
                   range=[0, 2.05]),
        yaxis=dict(title="Density", color="#999", gridcolor="#1a1a1a"),
        showlegend=False, font=dict(color="#999"))
    st.plotly_chart(f, use_container_width=True, key="hist")

# ─────────────────────────────────────────────
# COMPARISON BAR (all 3 methods)
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📊 All Three Methods — Side by Side")

names, sim_p, colors = [], [], []
for m, fn in METHODS.items():
    r2 = np.random.default_rng(seed)
    *_, lens = fn(n_chords, r2)
    names.append(m)
    sim_p.append((lens > SIDE_LENGTH).mean())
    colors.append(METHOD_INFO[m]["color"])
theo_p = [METHOD_INFO[m]["theory"] for m in names]

fbar = go.Figure()
fbar.add_trace(go.Bar(x=names, y=sim_p, marker_color=colors, opacity=0.9,
               name="Simulated", text=[f"{p:.4f}" for p in sim_p],
               textposition="outside", textfont=dict(color="white", size=13)))
fbar.add_trace(go.Bar(x=names, y=theo_p, marker_color=colors, opacity=0.35,
               name="Theoretical", text=[f"{p:.4f}" for p in theo_p],
               textposition="outside", textfont=dict(color="#aaa", size=13)))
fbar.update_layout(
    paper_bgcolor="#0d0d0d", plot_bgcolor="#0d0d0d", height=340,
    barmode="group", margin=dict(l=20, r=20, t=20, b=20),
    xaxis=dict(color="#ccc", tickfont=dict(size=13)),
    yaxis=dict(title="Probability", color="#999", gridcolor="#1a1a1a",
               range=[0, 0.72]),
    legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
    font=dict(color="#999"))
st.plotly_chart(fbar, use_container_width=True, key="bar")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center;color:#444;font-size:0.8rem;margin-top:30px;'>"
    "Bertrand's Paradox (1889) · Probability &amp; Statistics · Group 8<br>"
    "Circle r = 1 | Threshold √3 ≈ 1.732 | Inscribed equilateral triangle side"
    "</div>", unsafe_allow_html=True)