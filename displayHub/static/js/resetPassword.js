function resetPassword() {
    // Get the input values
    var newPassword = document.querySelector("input[name='new-password']").value;
    var confirmPassword = document.querySelector("input[name='confirm-password']").value;

    // Basic validation
    if (newPassword === "" || confirmPassword === "") {
        alert("Please fill in both password fields.");
        return;
    }

    if (newPassword !== confirmPassword) {
        alert("Passwords do not match.");
        return;
    }

    // You can add more complex validation here if needed

    // Logic for password reset (e.g., send a request to the server)
    // For now, just show a success message
    alert("Your password has been reset successfully.");

    // Redirect to login page or another page after success
    window.location.href = "/login/";  // Adjust this path to your actual login page
}
