window.switchTab = (id) => {
    // ซ่อนเนื้อหาทุกแท็บ
    document.querySelectorAll(".tab-content").forEach((element) => {
        element.classList.add("hidden");
    });

    // แสดงแท็บที่เลือก
    const targetTab = document.getElementById(`tab-${id}`);
    if (targetTab) {
        targetTab.classList.remove("hidden");
    }

    // จัดการเปลี่ยนสีและกรอบไฮไลท์ของปุ่มเมนูทั้งหมด
    document.querySelectorAll(".tab-btn").forEach((btn) => {
        btn.classList.remove("bg-blue-50", "dark:bg-zinc-800", "text-blue-600", "dark:text-blue-400");
        btn.classList.add("text-stone-600", "dark:text-zinc-300", "hover:bg-stone-100", "dark:hover:bg-zinc-800");
    });

    // ใส่ไฮไลท์เฉพาะปุ่มที่ถูกคลิก
    const activeBtn = document.getElementById(`nav-${id}`);
    if (activeBtn) {
        activeBtn.classList.remove("text-stone-600", "dark:text-zinc-300", "hover:bg-stone-100", "dark:hover:bg-zinc-800");
        activeBtn.classList.add("bg-blue-50", "dark:bg-zinc-800", "text-blue-600", "dark:text-blue-400");
    }
};
