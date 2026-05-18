# Bertrand's Paradox — Interactive Simulator

<p align="center">
  <em>Same question · Three different methods · Three different answers</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white" alt="NumPy" />
  <img src="https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white" alt="Plotly" />
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/raajpatre/bertrand-paradox?style=for-the-badge&color=FFD700" alt="Stars" />
  <img src="https://img.shields.io/github/last-commit/raajpatre/bertrand-paradox?style=for-the-badge&color=FF4B4B" alt="Last Commit" />
  <img src="https://img.shields.io/badge/Live_Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live Demo" />
</p>

<p align="center">
  <a href="https://bertrand-paradox-rvggxz7fjebv8m55drbfyy.streamlit.app">🚀 Live Demo</a> ·
  <a href="#-the-paradox">The Paradox</a> ·
  <a href="#-features">Features</a> ·
  <a href="#-run-locally">Run Locally</a>
</p>

---

## 📸 Gallery

<table>
  <tr>
    <td align="center"><strong>Simulator — Hero View</strong></td>
    <td align="center"><strong>Chord Visualisation + Histogram</strong></td>
  </tr>
  <tr>
    <td><img width="1503" height="787" alt="Screenshot 2026-05-18 at 8 45 23 AM" src="https://github.com/user-attachments/assets/0ab39101-bcc7-4073-9073-a8e7cdefa603" /></td>
    <td><img width="1088" height="489" alt="Screenshot 2026-05-18 at 8 46 55 AM" src="https://github.com/user-attachments/assets/f6625429-53cd-4491-aeed-a3ad2f135772" /></td>
  </tr>
  <tr>
    <td align="center" colspan="2"><strong>All Three Methods — Side by Side</strong></td>
  </tr>
  <tr>
    <td colspan="2"><img width="1496" height="804" alt="Screenshot 2026-05-18 at 8 45 58 AM" src="https://github.com/user-attachments/assets/b92afc2d-8ac5-4174-8000-36ca6e4bde50" /></td>
  </tr>
</table>

---

## 🎲 The Paradox

In 1889, French mathematician Joseph Bertrand asked a simple question:

> *"What is the probability that a random chord drawn inside a unit circle is longer than the side of the inscribed equilateral triangle?"*

He then showed something unsettling: **the answer depends entirely on what you mean by "random."**

Three equally valid geometric interpretations — each with a rigorous mathematical justification — produce three different probabilities:

| Method | How randomness is defined | Theoretical P |
|---|---|---|
| **Random Endpoints** | Pick 2 random points on the circumference | **1/3 ≈ 0.333** |
| **Random Radius** | Pick a random radius, then a random point on it | **1/2 = 0.500** |
| **Random Midpoint** | Pick a random point inside the circle as the chord's midpoint | **1/4 = 0.250** |

The paradox isn't a flaw in probability — it's a demonstration that *the phrase "at random" is meaningless without a precise sampling method*. This simulator makes that abstract insight visceral and visual.

---

## ✨ Features

- **Three simulation methods** — endpoints, radius, and midpoint, each implemented as a distinct geometric sampling algorithm
- **Interactive controls** — adjust chord count (10–2000), pick a random seed, and regenerate on demand
- **Live chord visualisation** — unit circle with long chords in red, short chords in grey, and the inscribed triangle threshold as a dashed reference
- **Chord length histogram** — density distribution with the √3 threshold marker
- **Real-time error tracking** — simulated probability vs theoretical value, |error| displayed per run
- **Side-by-side comparison** — all three methods plotted together, simulated vs theoretical
- **Dark custom UI** — styled with custom Streamlit CSS, no default Streamlit chrome

---

## 🛠️ Stack

| Layer | Choice |
|---|---|
| App framework | Streamlit |
| Numerical simulation | NumPy |
| Visualisation | Plotly (graph_objects + subplots) |
| Language | Python 3 |
| Hosting | Streamlit Community Cloud |

---

## 🚀 Run Locally

### Prerequisites

- Python 3.8+

### Installation

```bash
git clone https://github.com/raajpatre/bertrand-paradox.git
cd bertrand-paradox
pip install -r requirements.txt
```

### Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

### Dev Container

A `.devcontainer` configuration is included for VS Code / GitHub Codespaces. Open the repo in VS Code → "Reopen in Container" for a zero-setup Python environment.

---

## 🧮 How Each Method Works

**Random Endpoints** — Two points are sampled uniformly on the unit circle's circumference. The chord connecting them is long if its length > √3 (the triangle's side length). Theoretical P = 1/3.

**Random Radius** — A radius is chosen at a random angle. A point is then chosen uniformly along that radius. The chord perpendicular to the radius at that point is long if the point lies within the inner half of the radius. Theoretical P = 1/2.

**Random Midpoint** — A point is chosen uniformly inside the circle disk. The unique chord having that point as its midpoint is long if the point lies within a circle of radius 1/2. Theoretical P = 1/4.

---

## 📄 License

MIT — open to use, learn from, and fork.

---

<p align="center">
  If this helped you understand the paradox, consider dropping a ⭐
</p>

<p align="center">
  <em>Built by <a href="https://github.com/raajpatre">raajpatre</a> · PnS Project · SVyasa University × Newton School of Technology</em>
</p>



