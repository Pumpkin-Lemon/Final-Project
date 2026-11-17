// เปลี่ยน Tab และสีเมนูที่เลือก
window.switchTab = tabName => {

    const validTabs = [
        'solver',
        'lessons',
        'architecture'
    ];

    if (!validTabs.includes(tabName)) return;

    // ซ่อนเนื้อหาทุก Tab
    document.querySelectorAll(".tab-content").forEach(section => {

        const isActive = section.id === `tab-${tabName}`;

        section.classList.toggle("hidden", !isActive);
        section.classList.toggle("block", isActive);

    });

    // เปลี่ยนสีเมนู Desktop และ Mobile
    document.querySelectorAll(".tab-btn[data-tab]").forEach(button => {

        const isActive = button.dataset.tab === tabName;

        button.classList.toggle("active", isActive);

        button.setAttribute(
            "aria-pressed",
            String(isActive)
        );

    });

};

document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    switchCodeFile("app");
});
