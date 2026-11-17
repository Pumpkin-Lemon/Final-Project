window.switchTab = id => {
    document.querySelectorAll(".tab-content").forEach(element => {
        element.classList.add("hidden");
    });

    document.getElementById(`tab-${id}`)?.classList.remove("hidden");
};

document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    switchCodeFile("app");
});

document.addEventListener("DOMContentLoaded", () => {
    if (typeof initTheme === "function") initTheme();
});
