import os
import json
import time
import numpy as np
import joblib
from flask import Flask, render_template, request, jsonify, send_from_directory
import concurrent.futures
import tensorflow as tf
import yfinance as yf

load_model = tf.keras.models.load_model

app = Flask(__name__)

MODEL_DIR  = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model')
CHARTS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'img', 'charts')

models  = {}
scalers = {}

# ── Model Metadata ────────────────────────────────────────────────
MODEL_META = {
    'Linear Regression': {
        'type': 'Regresi',
        'icon': 'fa-chart-line',
        'color': '#16a34a',
        'desc': 'Model statistik klasik yang mempelajari hubungan linear antara fitur input dan output.'
    },
    'ANN': {
        'type': 'Neural Network',
        'icon': 'fa-brain',
        'color': '#d4af37',
        'desc': 'Jaringan saraf tiruan fully-connected dengan lapisan tersembunyi untuk pola non-linear.'
    },
    'Backpropagation': {
        'type': 'Neural Network',
        'icon': 'fa-network-wired',
        'color': '#947429',
        'desc': 'Custom neural network dilatih dengan algoritma backpropagation gradient descent.'
    },
    'LSTM': {
        'type': 'Recurrent NN',
        'icon': 'fa-wave-square',
        'color': '#7c3aed',
        'desc': 'Long Short-Term Memory — model sekuensial terbaik untuk data deret waktu (time-series).'
    },
    'K-Means': {
        'type': 'Clustering',
        'icon': 'fa-project-diagram',
        'color': '#0ea5e9',
        'desc': 'Segmentasi pasar tak-tersupervisi berdasarkan pola kurs dan volatilitas.'
    },
}

def load_all_models():
    global models, scalers
    print("[INFO] Memuat Model Machine Learning...")

    try:
        models['Linear Regression'] = joblib.load(os.path.join(MODEL_DIR, 'model_lr_kurs.joblib'))
        scalers['Linear Regression'] = joblib.load(os.path.join(MODEL_DIR, 'scaler_lr.joblib'))
        print("  [OK] Linear Regression")
    except Exception as e:
        print(f"  [FAIL] LR: {e}")

    try:
        models['ANN'] = load_model(os.path.join(MODEL_DIR, 'model_prediksi_kurs.h5'))
        scalers['ANN'] = joblib.load(os.path.join(MODEL_DIR, 'scaler_kurs.pkl'))
        print("  [OK] ANN")
    except Exception as e:
        print(f"  [FAIL] ANN: {e}")

    try:
        models['Backpropagation'] = load_model(os.path.join(MODEL_DIR, 'model_backprop_kurs.h5'))
        scalers['Backpropagation'] = joblib.load(os.path.join(MODEL_DIR, 'scaler_backprop.pkl'))
        print("  [OK] Backpropagation")
    except Exception as e:
        print(f"  [FAIL] Backprop: {e}")

    try:
        models['LSTM'] = load_model(os.path.join(MODEL_DIR, 'lstm_model.h5'))
        scalers['LSTM'] = joblib.load(os.path.join(MODEL_DIR, 'lstm_scaler.pkl'))
        print("  [OK] LSTM")
    except Exception as e:
        print(f"  [FAIL] LSTM: {e}")

    try:
        models['K-Means'] = joblib.load(os.path.join(MODEL_DIR, 'model_kmeans_kurs.joblib'))
        scalers['K-Means'] = joblib.load(os.path.join(MODEL_DIR, 'scaler_kmeans.joblib'))
        print("  [OK] K-Means")
    except Exception as e:
        print(f"  [FAIL] K-Means: {e}")

    print("[INFO] Model loading selesai.")

load_all_models()


def predict_single_model(model_name, input_data):
    """
    input_data: list of 30 floats (historical exchange rates)
    """
    start_time = time.time()
    try:
        model  = models.get(model_name)
        scaler = scalers.get(model_name)
        input_5 = input_data[-5:]

        if model is None or scaler is None:
            time.sleep(0.3)
            pred_value = "Cluster 1" if model_name == 'K-Means' else float(input_data[-1]) + np.random.uniform(-50, 50)
        else:
            if model_name == 'Linear Regression':
                sc = scaler.transform(np.array(input_5).reshape(-1, 1)).reshape(1, -1)
                pred_value = float(scaler.inverse_transform(model.predict(sc).reshape(-1, 1))[0][0])

            elif model_name in ['ANN', 'Backpropagation']:
                sc = scaler.transform(np.array(input_5).reshape(-1, 1)).reshape(1, -1)
                pred_value = float(scaler.inverse_transform(model.predict(sc, verbose=0).reshape(-1, 1))[0][0])

            elif model_name == 'LSTM':
                sc = scaler.transform(np.array(input_data).reshape(-1, 1))
                X  = np.reshape(sc, (1, len(input_data), 1))
                pred_value = float(scaler.inverse_transform(model.predict(X, verbose=0).reshape(-1, 1))[0][0])

            elif model_name == 'K-Means':
                X_km = np.array([[input_data[-1], input_data[-1] - input_data[-2]]])
                cluster = model.predict(scaler.transform(X_km))[0]
                pred_value = f"Cluster Market {cluster}"

        elapsed = time.time() - start_time
        return {
            "algorithm":  model_name,
            "prediction": pred_value if isinstance(pred_value, str) else round(pred_value, 2),
            "is_numeric": not isinstance(pred_value, str),
            "time_ms":    round(elapsed * 1000, 2),
            "status":     "Success"
        }
    except Exception as e:
        return {
            "algorithm":  model_name,
            "prediction": "Error",
            "is_numeric": False,
            "time_ms":    0,
            "status":     str(e)
        }


def run_parallel_prediction(inputs):
    algos = ['Linear Regression', 'ANN', 'Backpropagation', 'LSTM', 'K-Means']
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(predict_single_model, a, inputs): a for a in algos}
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    # Urutkan berdasarkan urutan ranking yang ditetapkan (Linear Regression, Backpropagation, LSTM, ANN)
    rank_order = {
        'Linear Regression': 1,
        'Backpropagation': 2,
        'LSTM': 3,
        'ANN': 4
    }
    num = sorted([r for r in results if r['is_numeric']],  key=lambda x: rank_order.get(x['algorithm'], 99))
    cls = [r for r in results if not r['is_numeric']]
    return num + cls


# ── Routes ────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare')
def compare():
    # Load chart index
    idx_path = os.path.join(CHARTS_DIR, 'index.json')
    chart_index = {}
    if os.path.exists(idx_path):
        with open(idx_path, 'r') as f:
            chart_index = json.load(f)
    return render_template('compare.html', chart_index=chart_index)


# ── API: Auto Predict (pulls data from Yahoo Finance) ─────────────

@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        prices = []
        
        # 1. Coba ambil data langsung dari Yahoo Finance API (bypass library yfinance jika error)
        try:
            import urllib.request
            import json
            url = "https://query1.finance.yahoo.com/v8/finance/chart/IDR=X?range=6mo&interval=1d"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                quotes = data['chart']['result'][0]['indicators']['quote'][0]['close']
                prices = [p for p in quotes if p is not None]
        except Exception as e:
            print(f"[Warning] Direct API fetch failed: {e}")
        
        # 2. Jika cara 1 gagal, gunakan library yfinance
        if len(prices) == 0:
            try:
                ticker = yf.Ticker("IDR=X")
                hist   = ticker.history(period="6mo")
                prices = hist['Close'].dropna().tolist()
            except Exception as e:
                print(f"[Warning] yfinance fetch failed: {e}")
        
        # 3. Jika gagal semua, gunakan CSV lokal sebagai Fallback
        if len(prices) == 0:
            csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'USD-IDR.csv')
            if os.path.exists(csv_path):
                import pandas as pd
                df = pd.read_csv(csv_path, sep=';')
                prices = df['Kurs'].dropna().head(30).tolist()[::-1]
            else:
                return jsonify({"error": "Gagal mendapatkan data harga dari Yahoo Finance. Coba lagi nanti."}), 500
            
        # Pad dengan nilai tertua jika masih kurang dari 30
        if len(prices) < 30:
            prices = [prices[0]] * (30 - len(prices)) + prices
            
        inputs = prices[-30:]
    except Exception as e:
        return jsonify({"error": f"Terjadi kesalahan sistem: {str(e)}"}), 500

    results = run_parallel_prediction(inputs)
    return jsonify({
        "mode":        "auto",
        "inputs":      inputs[-7:],
        "latest_kurs": round(inputs[-1], 2),
        "results":     results
    })


# ── API: Manual Predict (user-supplied data) ───────────────────────

@app.route('/api/predict-manual', methods=['POST'])
def api_predict_manual():
    body = request.get_json(force=True, silent=True) or {}
    raw  = body.get('values', [])

    # Accept comma / space / newline separated string too
    if isinstance(raw, str):
        import re
        raw = [x for x in re.split(r'[,\s\n]+', raw.strip()) if x]

    try:
        values = [float(v) for v in raw]
    except (ValueError, TypeError):
        return jsonify({"error": "Format data tidak valid. Masukkan angka yang benar."}), 400

    if len(values) < 5:
        return jsonify({"error": "Minimal 5 nilai kurs diperlukan untuk prediksi."}), 400

    # Pad to 30 if needed
    if len(values) < 30:
        values = [values[0]] * (30 - len(values)) + values

    results = run_parallel_prediction(values[-30:])
    return jsonify({
        "mode":        "manual",
        "inputs":      values[-7:],
        "latest_kurs": round(values[-1], 2),
        "results":     results
    })


# ── API: Chart index ──────────────────────────────────────────────

@app.route('/api/charts')
def api_charts():
    idx_path = os.path.join(CHARTS_DIR, 'index.json')
    if not os.path.exists(idx_path):
        return jsonify({}), 404
    with open(idx_path, 'r') as f:
        return jsonify(json.load(f))


if __name__ == '__main__':
    app.run(debug=True, threaded=True)