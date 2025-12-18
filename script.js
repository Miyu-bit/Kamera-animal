const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const resultDiv = document.getElementById('result');
const captureBtn = document.getElementById('capture');

// Akses kamera
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => { video.srcObject = stream; })
    .catch(err => console.error('Error accessing camera:', err));

captureBtn.addEventListener('click', () => {
    const ctx = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);
    
    canvas.toBlob(blob => {
        const formData = new FormData();
        formData.append('image', blob, 'capture.jpg');
        
        fetch('http://localhost:5000/analyze', { method: 'POST', body: formData })
            .then(response => response.json())
            .then(data => {
                resultDiv.innerHTML = `
                    <h2>Hewan Ditemukan: ${data.animal}</h2>
                    <p>Keyakinan: ${(data.confidence * 100).toFixed(2)}%</p>
                    <p>Habitat: ${data.info.habitat}</p>
                    <p>Fakta: ${data.info.fact}</p>
                    <p>Suara: ${data.info.sound}</p>
                `;
                // Tambahkan suara (opsional): new Audio('sounds/${data.info.sound}.mp3').play();
            })
            .catch(err => console.error('Error:', err));
    });
});