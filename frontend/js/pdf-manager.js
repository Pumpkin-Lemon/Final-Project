(() => {
    // Public Frontend must not upload or index PDF files.
    // PDF indexing remains an administrator/backend responsibility.

    window.initPDFManager = () => {};

    window.selectPDFModule = () => {
        console.warn("PDF Manager is disabled in the public interface.");
    };

    window.handlePDFUpload = event => {
        if (event?.target) {
            event.target.value = "";
        }

        alert("ไม่อนุญาตให้อัปโหลด PDF ผ่านหน้าผู้ใช้ทั่วไป");
    };
})();
