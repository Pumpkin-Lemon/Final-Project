window.switchTab = (id) => {
    // 1. ซ่อนเนื้อหาทุกแท็บ
    document.querySelectorAll(".tab-content").forEach((element) => {
        element.classList.add("hidden");
    });

    // แสดงแท็บเนื้อหาที่ถูกเลือก
    const targetTab = document.getElementById(`tab-${id}`);
    if (targetTab) {
        targetTab.classList.remove("hidden");
    }

    // 2. ล้างค่าไฮไลท์ของปุ่มเมนูทั้งหมด
    document.querySelectorAll(".tab-btn").forEach((btn) => {
        btn.classList.remove("bg-blue-50", "dark:bg-zinc-800", "text-blue-600", "dark:text-blue-400", "font-medium");
        btn.classList.add("text-stone-600", "dark:text-zinc-300", "hover:bg-stone-100", "dark:hover:bg-zinc-800");
    });

    // 3. ใส่ไฮไลท์เฉพาะปุ่มที่ถูกคลิก (รองรับทั้ง Desktop และ Mobile)
    document.querySelectorAll(`.tab-btn[onclick*="${id}"]`).forEach((activeBtn) => {
        activeBtn.classList.remove("text-stone-600", "dark:text-zinc-300", "hover:bg-stone-100", "dark:hover:bg-zinc-800");
        activeBtn.classList.add("bg-blue-50", "dark:bg-zinc-800", "text-blue-600", "dark:text-blue-400", "font-medium");
    });
};

document.addEventListener("DOMContentLoaded", () => {
    if (typeof initTheme === "function") initTheme();
});
