document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");

  form.addEventListener("submit", function (e) {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const role = document.getElementById("role").value;

    if (!email || !password || !role) {
      alert("Please fill in all fields.");
      e.preventDefault(); // Stop the form from submitting
    } else {
      alert(`Logging in as ${role}`);
    }
  });
});
