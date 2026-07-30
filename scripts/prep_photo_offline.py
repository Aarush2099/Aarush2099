"""
Offline variant of prep_photo.py: uses OpenCV GrabCut for background removal
instead of rembg (which needs a network download for its model), then applies
the same CLAHE local-contrast + white-composite pipeline.

    python scripts/prep_photo_offline.py <input.jpg> [output.png]
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.jpg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")

bgr = cv2.imread(INP)
h, w = bgr.shape[:2]

# 1. GrabCut background removal, seeded with a generous centered rect
mask = np.zeros((h, w), np.uint8)
bgd_model = np.zeros((1, 65), np.float64)
fgd_model = np.zeros((1, 65), np.float64)
margin_x, margin_top, margin_bottom = int(w * 0.08), int(h * 0.03), int(h * 0.15)
rect = (margin_x, margin_top, w - 2 * margin_x, h - margin_top - margin_bottom)
cv2.grabCut(bgr, mask, rect, bgd_model, fgd_model, 8, cv2.GC_INIT_WITH_RECT)
alpha = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
alpha = cv2.GaussianBlur(alpha, (0, 0), 2.0)

rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

# 2. local-contrast the luminance (CLAHE)
gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
clahe = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(8, 8))
gray = clahe.apply(gray)
gray = cv2.convertScaleAbs(gray, alpha=1.05, beta=18)

# 3. paste onto white using the alpha mask
maskf = (alpha.astype(np.float32) / 255.0)
out = gray.astype(np.float32) * maskf + 255.0 * (1.0 - maskf)
out = np.clip(out, 0, 255).astype(np.uint8)

Image.fromarray(out, mode="L").save(OUT)
print("wrote", OUT, out.shape)
