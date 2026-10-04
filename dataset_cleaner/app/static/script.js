document.getElementById('btn-analyze').addEventListener('click', async () => {
    const inputDir = document.getElementById('input_dir').value;
    const analysisSection = document.getElementById('analysis-section');
    const resultsDiv = document.getElementById('analysis-results');

    analysisSection.style.display = 'block';
    resultsDiv.innerHTML = 'Analiz yapılıyor, lütfen bekleyin...';

    const formData = new FormData();
    formData.append('input_dir', inputDir);

    try {
        const response = await fetch('/api/analyze', { method: 'POST', body: formData });
        const data = await response.json();

        let html = `<div class="stat-grid">
            <div class="stat-box"><div class="stat-value">${data.total_files}</div><div class="stat-label">Toplam Dosya</div></div>
            <div class="stat-box"><div class="stat-value">${data.supported_files}</div><div class="stat-label">Desteklenen Dosya</div></div>
            <div class="stat-box"><div class="stat-value">${(data.total_bytes / 1024 / 1024).toFixed(2)} MB</div><div class="stat-label">Toplam Boyut</div></div>
        </div>`;
        resultsDiv.innerHTML = html;
    } catch (e) {
        resultsDiv.innerHTML = 'Hata oluştu: ' + e;
    }
});

document.getElementById('btn-build').addEventListener('click', async () => {
    const inputDir = document.getElementById('input_dir').value;
    const outputDir = document.getElementById('output_dir').value;
    const statusSection = document.getElementById('status-section');
    const statusDiv = document.getElementById('status-results');

    statusSection.style.display = 'block';
    statusDiv.innerHTML = 'Dataset inşası başlatıldı...';

    const formData = new FormData();
    formData.append('input_dir', inputDir);
    formData.append('output_dir', outputDir);

    try {
        const response = await fetch('/api/build', { method: 'POST', body: formData });
        const data = await response.json();

        let html = `<h3>Durum: ${data.status}</h3><div class="stat-grid">
            <div class="stat-box"><div class="stat-value">${data.processed_documents}</div><div class="stat-label">İşlenen Doküman</div></div>
            <div class="stat-box"><div class="stat-value">${data.accepted_documents}</div><div class="stat-label">Kabul Edilen</div></div>
            <div class="stat-box"><div class="stat-value">${data.rejected_documents}</div><div class="stat-label">Reddedilen</div></div>
            <div class="stat-box"><div class="stat-value">${data.exact_duplicates}</div><div class="stat-label">Birebir Kopya</div></div>
            <div class="stat-box"><div class="stat-value">${data.near_duplicates}</div><div class="stat-label">Yakın Kopya</div></div>
            <div class="stat-box"><div class="stat-value">${data.train_documents}</div><div class="stat-label">Train</div></div>
            <div class="stat-box"><div class="stat-value">${data.validation_documents}</div><div class="stat-label">Validation</div></div>
            <div class="stat-box"><div class="stat-value">${data.test_documents}</div><div class="stat-label">Test</div></div>
        </div>`;
        statusDiv.innerHTML = html;
    } catch (e) {
        statusDiv.innerHTML = 'Hata oluştu: ' + e;
    }
});
