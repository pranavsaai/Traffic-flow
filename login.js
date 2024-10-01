document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();

    // Retrieve stored credentials
    const storedEmail = localStorage.getItem('signupEmail');
    const storedPassword = localStorage.getItem('signupPassword');

    // Check credentials
    if ((email === storedEmail && password === storedPassword) || 
        (email === 'pkuchipu2@gitam.in' && password === 'Pranav@2004')) {
        // Store login status in localStorage
        localStorage.setItem('loggedIn', 'true');
        // Redirect to the main content page
        window.location.href = 'sidebar.html';
    } else {
        alert('Invalid credentials. Please try again.');
    }
});