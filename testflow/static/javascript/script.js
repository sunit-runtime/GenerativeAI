window.onload = function () {
    const errorMessage = document.getElementById('error-message');
    if (errorMessage) {
        setInterval(() => {
            errorMessage.innerHTML = '&nbsp;';
        }, 5000);
    }
};