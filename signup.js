document.getElementById('signupForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    const newEmail = document.getElementById('newEmail').value.trim();
    const newPassword = document.getElementById('newPassword').value.trim();

    // Validate that both fields are filled
    if (newEmail && newPassword) {
        // Save new credentials in localStorage
        localStorage.setItem('signupEmail', newEmail);
        localStorage.setItem('signupPassword', newPassword);

        // Redirect to the login page
        window.location.href = 'login.html';
    } else {
        alert('Please enter both email and password.');
    }
});