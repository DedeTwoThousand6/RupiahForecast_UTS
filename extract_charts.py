"""
Extract all chart/image outputs from Jupyter notebooks
and save them to app/static/img/charts/
"""
import json, base64, os

NOTEBOOKS = {
    'ann': 'd:/UTS AI/notebook/ann.ipynb',
    'backpropagation': 'd:/UTS AI/notebook/backpropagation.ipynb',
    'kmeans': 'd:/UTS AI/notebook/k-means.ipynb',
    'regresi_linear': 'd:/UTS AI/notebook/regresi_linear.ipynb',
    'rnn': 'd:/UTS AI/notebook/rnn.ipynb',
}

OUT_DIR = 'd:/UTS AI/app/static/img/charts'
os.makedirs(OUT_DIR, exist_ok=True)

index = {}

for key, path in NOTEBOOKS.items():
    print(f"\n[{key}] Reading {path}...")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
    except Exception as e:
        print(f"  ERROR reading: {e}")
        continue

    cells = nb.get('cells', [])
    img_num = 0
    index[key] = []

    for cell_i, cell in enumerate(cells):
        outputs = cell.get('outputs', [])
        for out in outputs:
            data = out.get('data', {})
            png = data.get('image/png', None)
            if png:
                # png may be a list of strings or a single string
                if isinstance(png, list):
                    png = ''.join(png)
                fname = f"{key}_{img_num}.png"
                fpath = os.path.join(OUT_DIR, fname)
                with open(fpath, 'wb') as imgf:
                    imgf.write(base64.b64decode(png))
                index[key].append(fname)
                print(f"  Saved: {fname}")
                img_num += 1

    print(f"  Total images: {img_num}")

# Save index JSON for use by Flask
idx_path = 'd:/UTS AI/app/static/img/charts/index.json'
with open(idx_path, 'w') as f:
    json.dump(index, f, indent=2)
print(f"\nIndex saved to {idx_path}")
print("\nDone!")
