document.addEventListener("DOMContentLoaded", () => {
  const loginButton = document.getElementById("login-button");

  loginButton.addEventListener("click", () => {
    window.location.href = "home";
  });
});
