async function processImage() {
    const fileInput = document.getElementById('imageUpload');
    const formData = new FormData();
    formData.append('image', fileInput.files[0]);

    const response = await fetch('/api/process', {
        method: 'POST',
        body: formData
    });
    const result = await response.json();
    document.getElementById('resultImage').src = result.imageUrl;
}