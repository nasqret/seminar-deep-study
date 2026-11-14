"""Generate the header graphics of the landing page: assets/hero.{webp,jpg}, og.png, favicon.png.

The picture should be the *result of a computation from the paper*, not decoration, and this
script is its reproducible source (it is published next to the image). Replace `compute()` with
the paper's object — an incidence graph of explicit curves, a fundamental domain, a plot of the
counted solutions — and keep the pattern:

1. compute the object exactly or in high precision, from the paper's explicit data (the same
   transcription as the numeric screen in artifacts/computational/);
2. CHECK it: assertions that stop the script if the picture would show something false (counts,
   degrees, symmetries, ranks), and, when the CAS computed the same object exactly (for example
   an incidence matrix in cas/out/), a cross-check against that transcript;
3. render it, blending the left edge into the page background so that the title stays readable;
4. export the sizes the page needs.

The placeholder computation is Newton's method for z^3 - 1: each pixel is a starting point,
coloured by the root it converges to; points that converge fast stay dark, and the basin
boundaries, where the method hesitates longest, glow. Its three colours
are the page's colours for numerics (amber), symbolic computation (indigo) and formal proof
(green). Write an "about the picture" section on the page saying what is shown.

Run from the project root:

    uv run --no-project --with numpy --with pillow python -I scripts/generate_hero.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
TITLE = "{{TITLE}}"                                  # used on the social-preview image
BG = np.array([11, 16, 32], dtype=float)             # page background behind the hero (#0b1020)
COLOURS = np.array([[245, 158, 11],                  # numerics: amber
                    [99, 102, 241],                  # symbolic / CAS: indigo
                    [16, 185, 129]], dtype=float)    # formal proof: green


def compute(width: int, height: int):
    """Placeholder: Newton basins of z^3 - 1. Returns (class index per pixel, shade in [0, 1])."""
    roots = np.exp(2j * np.pi * np.arange(3) / 3)
    xs = np.linspace(-1.9, 1.9, width)
    ys = np.linspace(1.9 * height / width, -1.9 * height / width, height)
    z = xs[None, :] + 1j * ys[:, None]
    steps = np.full(z.shape, 60.0)
    for k in range(60):
        with np.errstate(divide="ignore", invalid="ignore"):
            z = z - (z**3 - 1) / (3 * z**2)
        near = np.min(np.abs(z[..., None] - roots), axis=-1) < 1e-6
        steps = np.where(near & (steps == 60), k, steps)
    idx = np.argmin(np.abs(np.nan_to_num(z)[..., None] - roots), axis=-1)
    # CHECKS: the roots are cube roots of unity, and almost every start converged.
    assert np.allclose(roots**3, 1)
    assert np.mean(steps < 60) > 0.95, "too many starting points did not converge"
    # slow convergence (the basin boundaries) glows; fast convergence stays dark
    return idx, np.clip(steps / 25.0, 0.0, 1.0) ** 0.8


def render(width: int, height: int, fade: bool = True, dither: bool = True) -> Image.Image:
    idx, shade = compute(width, height)
    rgb = BG + (COLOURS[idx] - BG) * (0.08 + 0.92 * shade[..., None])
    if fade:   # blend the left part into the background so that the title stays readable
        t = np.clip(np.linspace(-0.2, 1.6, width), 0, 1) ** 1.4
        rgb = BG + (rgb - BG) * t[None, :, None]
    if dither:  # a little noise removes banding in JPEG/WebP (PNG would grow, so not there)
        rgb += np.random.default_rng(0).uniform(-1.5, 1.5, rgb.shape)
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB")


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    hero = render(1600, 900)
    hero.save(ASSETS / "hero.webp", quality=88)
    hero.save(ASSETS / "hero.jpg", quality=88)
    og = render(1200, 630, dither=False)
    draw = ImageDraw.Draw(og)
    try:
        font = ImageFont.load_default(size=44)
    except TypeError:                                 # Pillow < 10.1
        font = ImageFont.load_default()
    draw.text((60, 270), TITLE, fill=(248, 250, 252), font=font)
    og.save(ASSETS / "og.png")
    render(256, 256, fade=False, dither=False).resize((64, 64), Image.LANCZOS).save(ASSETS / "favicon.png")
    print("wrote", ", ".join(p.name for p in sorted(ASSETS.glob("*"))))


if __name__ == "__main__":
    main()
