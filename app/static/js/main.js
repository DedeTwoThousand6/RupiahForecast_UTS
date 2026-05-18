let chartInstance = null;
let histChartInstance = null;
let currentResults = null;

/* =============================================
   RENDER RANKING CARDS
   ============================================= */
function renderResults(results) {
    const container = document.getElementById('rankingContainer');
    if (!container) return;
    container.innerHTML = '';

    const medals = ['🥇', '🥈', '🥉'];
    let rankIndex = 0;

    results.forEach((res) => {
        const isNumeric = res.is_numeric;
        const isTop = isNumeric && rankIndex === 0;
        const isCluster = !isNumeric;
        const medal = isNumeric && rankIndex < 3 ? medals[rankIndex] : isNumeric ? `#${rankIndex + 1}` : '📊';
        const predText = isNumeric ? 'Rp ' + res.prediction.toLocaleString('id-ID') : res.prediction;
        const cardClass = isTop ? 'rank-card top' : isCluster ? 'rank-card cluster' : 'rank-card';
        const tagHTML = isTop
            ? `<div class="rank-tag gold-tag">TOP PREDICTION</div>`
            : isCluster
                ? `<div class="rank-tag purple-tag">MARKET INSIGHT</div>`
                : '';
        const statusClass = res.status === 'Success' ? 'rank-status success' : 'rank-status error';
        const statusIcon = res.status === 'Success' ? '✔' : '✖';
        
        container.innerHTML += `
            <div class="${cardClass}">
                ${tagHTML}
                <div class="rank-algo">${medal} ${res.algorithm}</div>
                <div class="rank-value">${predText}</div>
                <div class="rank-footer">
                    <span>⏱ ${res.time_ms} ms</span>
                    <span class="${statusClass}">${statusIcon} ${res.status}</span>
                </div>
            </div>
        `;
        if (isNumeric) rankIndex++;
    });
}

/* =============================================
   RENDER PREDICTION BAR CHART
   ============================================= */
function renderChart(results) {
    const numeric = results.filter(r => r.is_numeric);
    if (!numeric.length) return;

    const labels = numeric.map(r => r.algorithm);
    const data = numeric.map(r => r.prediction);
    const minVal = Math.min(...data);
    const maxVal = Math.max(...data);

    const options = {
        series: [{ name: 'Prediksi Kurs (Rp)', data }],
        chart: {
            type: 'bar', height: 300,
            foreColor: '#5c4f31',
            toolbar: { show: false },
            background: 'transparent',
            animations: { enabled: true, easing: 'easeinout', speed: 800 }
        },
        plotOptions: { bar: { borderRadius: 6, columnWidth: '50%' } },
        dataLabels: {
            enabled: true,
            formatter: v => 'Rp ' + v.toLocaleString('id-ID'),
            style: { fontSize: '11px', colors: ['#5c4f31'] },
            offsetY: -6
        },
        xaxis: {
            categories: labels,
            axisBorder: { color: 'rgba(212,175,55,0.2)' },
            axisTicks: { color: 'rgba(212,175,55,0.2)' },
            labels: {
                hideOverlappingLabels: false,
                trim: true,
                style: {
                    fontSize: '10px'
                }
            }
        },
        yaxis: {
            min: minVal - 200, max: maxVal + 200,
            labels: { formatter: v => 'Rp ' + v.toLocaleString('id-ID') }
        },
        colors: ['#d4af37'],
        fill: {
            type: 'gradient',
            gradient: { shade: 'light', type: 'vertical', gradientToColors: ['#947429'], opacityFrom: 1, opacityTo: 0.85 }
        },
        grid: { borderColor: 'rgba(212,175,55,0.15)', strokeDashArray: 4 },
        tooltip: { theme: 'light', y: { formatter: v => 'Rp ' + v.toLocaleString('id-ID') } }
    };

    if (chartInstance) chartInstance.destroy();
    chartInstance = new ApexCharts(document.querySelector('#predictionChart'), options);
    chartInstance.render();
}

/* =============================================
   RENDER HISTORY LINE CHART
   ============================================= */
function renderHistoryChart(inputs) {
    const el = document.querySelector('#historyChart');
    if (!el || !inputs || !inputs.length) return;

    const labels = inputs.map((_, i) => `H-${inputs.length - 1 - i}`);
    labels[labels.length - 1] = 'Hari Ini';

    const options = {
        series: [{ name: 'Kurs (Rp)', data: inputs.map(v => parseFloat(v.toFixed(2))) }],
        chart: {
            type: 'area', height: 220,
            foreColor: '#5c4f31',
            toolbar: { show: false },
            background: 'transparent',
            animations: { enabled: true, easing: 'easeinout', speed: 700 }
        },
        stroke: { curve: 'smooth', width: 2.5 },
        fill: {
            type: 'gradient',
            gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0.05, stops: [0, 100] }
        },
        xaxis: {
            categories: labels,
            axisBorder: { color: 'rgba(212,175,55,0.2)' },
            axisTicks: { color: 'rgba(212,175,55,0.2)' },
            labels: { style: { fontSize: '11px' } }
        },
        yaxis: {
            labels: { formatter: v => 'Rp ' + v.toLocaleString('id-ID') }
        },
        colors: ['#947429'],
        grid: { borderColor: 'rgba(212,175,55,0.15)', strokeDashArray: 4 },
        dataLabels: { enabled: false },
        markers: { size: 4, colors: ['#d4af37'], strokeWidth: 0 },
        tooltip: { theme: 'light', y: { formatter: v => 'Rp ' + v.toLocaleString('id-ID') } }
    };

    if (histChartInstance) histChartInstance.destroy();
    histChartInstance = new ApexCharts(el, options);
    histChartInstance.render();
}

/* =============================================
   MAIN DASHBOARD RESULT RENDERER
   ============================================= */
function renderDashboardResult(data) {
    renderResults(data.results);
    renderChart(data.results);
    if (data.inputs) renderHistoryChart(data.inputs);
}

/* =============================================
   EXPORT CSV
   ============================================= */
function exportCSV() {
    if (!currentResults) {
        alert('Lakukan prediksi terlebih dahulu!');
        return;
    }
    let csv = 'data:text/csv;charset=utf-8,Algoritma,Prediksi/Insight,Waktu Eksekusi (ms),Status\n';
    currentResults.forEach(row => {
        csv += `${row.algorithm},${row.prediction},${row.time_ms},${row.status}\n`;
    });
    const link = document.createElement('a');
    link.setAttribute('href', encodeURI(csv));
    link.setAttribute('download', 'prediksi_rupiah_ai.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/* =============================================
   INTERCEPT FETCH TO STORE RESULTS
   ============================================= */
document.addEventListener('DOMContentLoaded', () => {
    const origFetch = window.fetch;
    window.fetch = async (...args) => {
        const res = await origFetch(...args);
        const url = typeof args[0] === 'string' ? args[0] : '';
        if (url.includes('/api/predict')) {
            res.clone().json().then(data => {
                if (data && data.results) currentResults = data.results;
            }).catch(() => { });
        }
        return res;
    };
});