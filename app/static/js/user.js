// Load user information in navbar
document.addEventListener('DOMContentLoaded', async function() {
  try {
    const response = await fetch('/api/current-user');
    const data = await response.json();

    const userNameEl = document.getElementById('userName');
    if (userNameEl && data.username) {
      userNameEl.textContent = data.username;
    }
  } catch (error) {
    console.error('Error loading user info:', error);
  }
});

