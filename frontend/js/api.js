(() => {
    const config = window.SCITUTOR_CONFIG;

    function validateAnalyzeResponse(data) {
        const expectedKeys = [
            "answer",
            "vars",
            "socraticCards",
            "steps",
            "pdfRef",
            "status",
            "citations"
        ];

        if (!data || typeof data !== "object" || Array.isArray(data)) {
            throw new Error("API Response ต้องเป็น Object");
        }

        const actualKeys = Object.keys(data);
        if (
            actualKeys.length !== expectedKeys.length ||
            expectedKeys.some(key => !Object.prototype.hasOwnProperty.call(data, key)) ||
            actualKeys.some(key => !expectedKeys.includes(key))
        ) {
            throw new Error("API Response มี Field ไม่ตรงกับ Response Contract");
        }

        const nonEmptyString = value =>
            typeof value === "string" && value.trim().length > 0;

        if (data.status !== "success") {
            throw new Error("API ไม่ได้ส่งสถานะ success");
        }

        if (!nonEmptyString(data.answer)) {
            throw new Error("Response Contract: answer ต้องเป็น String ที่ไม่ว่าง");
        }

        if (!nonEmptyString(data.pdfRef)) {
            throw new Error("Response Contract: pdfRef ต้องเป็น String ที่ไม่ว่าง");
        }

        if (!Array.isArray(data.vars)) {
            throw new Error("Response Contract: vars ต้องเป็น Array");
        }

        for (const item of data.vars) {
            if (
                !item ||
                typeof item !== "object" ||
                Array.isArray(item) ||
                Object.keys(item).length !== 2 ||
                !Object.prototype.hasOwnProperty.call(item, "name") ||
                !Object.prototype.hasOwnProperty.call(item, "val") ||
                !nonEmptyString(item.name) ||
                !nonEmptyString(item.val)
            ) {
                throw new Error("Response Contract: vars item ไม่ถูกต้อง");
            }
        }

        if (!Array.isArray(data.socraticCards)) {
            throw new Error("Response Contract: socraticCards ต้องเป็น Array");
        }

        for (const item of data.socraticCards) {
            if (
                !item ||
                typeof item !== "object" ||
                Array.isArray(item) ||
                Object.keys(item).length !== 3 ||
                !nonEmptyString(item.question) ||
                !nonEmptyString(item.hint) ||
                !nonEmptyString(item.checkpoint)
            ) {
                throw new Error("Response Contract: socraticCards item ไม่ถูกต้อง");
            }
        }

        if (!Array.isArray(data.steps)) {
            throw new Error("Response Contract: steps ต้องเป็น Array");
        }

        for (const item of data.steps) {
            if (
                !item ||
                typeof item !== "object" ||
                Array.isArray(item) ||
                Object.keys(item).length !== 2 ||
                !nonEmptyString(item.title) ||
                !nonEmptyString(item.detail)
            ) {
                throw new Error("Response Contract: steps item ไม่ถูกต้อง");
            }
        }

        if (!Array.isArray(data.citations)) {
            throw new Error("Response Contract: citations ต้องเป็น Array");
        }

        for (const item of data.citations) {
            if (
                !item ||
                typeof item !== "object" ||
                Array.isArray(item) ||
                Object.keys(item).length !== 2 ||
                !nonEmptyString(item.source_file) ||
                !(
                    (typeof item.page === "string" && nonEmptyString(item.page)) ||
                    (typeof item.page === "number" && Number.isInteger(item.page))
                )
            ) {
                throw new Error("Response Contract: citations item ไม่ถูกต้อง");
            }
        }

        return data;
    }

    async function req(path, options = {}) {
        const response = await fetch(
            `${config.API_BASE_URL}${config.API_VERSION}${path}`,
            options
        );

        let data;
        try {
            data = await response.json();
        } catch {
            throw new Error(`เซิร์ฟเวอร์ส่งข้อมูลที่ไม่ใช่ JSON (HTTP ${response.status})`);
        }

        if (!response.ok) {
            const detail =
                data && typeof data.detail === "string"
                    ? data.detail
                    : `HTTP ${response.status}`;
            throw new Error(detail);
        }

        return data;
    }

    window.SciTutorAPI = {
        validateAnalyzeResponse,

        analyze: async question => {
            const data = await req("/analyze-with-pdf-rag", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question })
            });

            return validateAnalyzeResponse(data);
        },

        survey: data => req("/survey", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        }),

        summary: () => req("/survey/summary")
    };
})();
