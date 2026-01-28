const btn = document.getElementById("themeToggle")

function applyTheme(t){
  document.body.classList.toggle("light", t === "light")
  localStorage.setItem("theme", t)
}

btn.onclick = () => {
  const current = localStorage.getItem("theme") || "dark"
  applyTheme(current === "dark" ? "light" : "dark")
}

applyTheme(localStorage.getItem("theme") || "dark")
