let timer = 45;
    let timerInterval;

    function startTimer() {
        timerInterval = setInterval(() => {
            if (timer > 0) {
                timer--;
                document.getElementById('timer').textContent = `${timer} seconds remaining`;
            } else {
                clearInterval(timerInterval);
                document.getElementById('sendOtpBtn').click();
            }
        }, 1000);
    }

    function sendOtp() {
        alert('OTP sent to your email.');
        timer = 45;
        document.getElementById('timer').textContent = `${timer} seconds remaining`;
        clearInterval(timerInterval);
        startTimer();
    }

    startTimer();