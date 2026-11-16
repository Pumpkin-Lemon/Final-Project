(() => {
    const $ = id => document.getElementById(id);

    window.handleFileSelect = event => {
        const file = event.target.files?.[0];
        if (!file) return;

        if (!file.type.startsWith("image/")) {
            alert("เลือกไฟล์รูปภาพเท่านั้น");
            return;
        }

        const reader = new FileReader();
        reader.onload = result => {
            $("image-preview").src = result.target.result;
            $("image-preview-container").classList.remove("hidden");
        };
        reader.readAsDataURL(file);
    };

    window.removeImage = event => {
        event?.stopPropagation();
        $("file-input").value = "";
        $("image-preview-container").classList.add("hidden");
    };

    window.loadPreset = id => {
        const preset = SCITUTOR_PRESETS[id];
        if (preset) {
            $("question-text").value = preset.text;
            processOCR();
        }
    };

    window.processOCR = async () => {
        const question = $("question-text")?.value.trim() || "";

        if (!question) {
            const hasImage = $("file-input")?.files?.length;
            alert(
                hasImage
                    ? "ระบบแสดงตัวอย่างภาพได้ แต่ยังไม่รองรับ OCR ภาพ กรุณาพิมพ์โจทย์ก่อน"
                    : "กรุณาพิมพ์โจทย์ก่อน"
            );
            return;
        }

        $("ocr-placeholder").classList.add("hidden");
        $("ocr-result").classList.add("hidden");
        $("ocr-loading").classList.remove("hidden");
        $("ocr-progress").style.width = "45%";

        try {
            const data = await SciTutorAPI.analyze(question);
            renderWorkbenchResults(data);

            $("ocr-loading").classList.add("hidden");
            $("ocr-result").classList.remove("hidden");
            $("ocr-progress").style.width = "100%";
        } catch (error) {
            $("ocr-loading").classList.add("hidden");
            $("ocr-placeholder").classList.remove("hidden");
            alert(`วิเคราะห์ไม่สำเร็จ: ${error.message}`);
        }
    };

    window.renderWorkbenchResults = data => {
        // Validate again at the rendering boundary.
        const validated = SciTutorAPI.validateAnalyzeResponse(data);

        const answer = $("answer-content");
        const variables = $("extracted-vars-grid");
        const citationPage = $("pdf-cite-page");
        const citations = $("citations-list");
        const cards = $("socratic-cards-container");
        const steps = $("solution-steps-container");

        const requiredElements = [
            answer, variables, citationPage, citations, cards, steps
        ];

        if (requiredElements.some(element => !element)) {
            throw new Error("ไม่พบ HTML element ที่จำเป็นสำหรับแสดงผล");
        }

        answer.textContent = validated.answer;

        variables.replaceChildren();
        validated.vars.forEach(item => {
            const element = document.createElement("div");
            element.className = "p-2 border rounded";
            element.textContent = `${item.name}: ${item.val}`;
            variables.append(element);
        });

        citationPage.textContent = validated.pdfRef;
        citations.replaceChildren();

        if (validated.citations.length === 0) {
            const empty = document.createElement("p");
            empty.className = "text-xs text-slate-500";
            empty.textContent = "ไม่พบรายการ Citation จากเอกสารที่ค้นคืน";
            citations.append(empty);
        } else {
            validated.citations.forEach(item => {
                const row = document.createElement("div");
                row.className = "p-2 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700";

                const source = document.createElement("p");
                source.className = "font-medium break-words";
                source.textContent = item.source_file;

                const page = document.createElement("p");
                page.className = "text-[11px] text-slate-500 mt-1";
                page.textContent = `หน้า ${item.page}`;

                row.append(source, page);
                citations.append(row);
            });
        }

        cards.replaceChildren();
        validated.socraticCards.forEach(item => {
            const element = document.createElement("div");
            element.className = "p-4 border rounded-xl space-y-2";

            for (const [label, value] of [
                ["คำถาม", item.question],
                ["คำใบ้", item.hint],
                ["จุดตรวจสอบความเข้าใจ", item.checkpoint]
            ]) {
                const paragraph = document.createElement("p");
                paragraph.className = "text-xs whitespace-pre-line";
                paragraph.textContent = `${label}: ${value}`;
                element.append(paragraph);
            }

            cards.append(element);
        });

        steps.replaceChildren();
        validated.steps.forEach(item => {
            const element = document.createElement("div");
            element.className = "p-3 border rounded-xl";

            const heading = document.createElement("b");
            heading.textContent = item.title;

            const detail = document.createElement("p");
            detail.className = "text-xs whitespace-pre-line mt-1";
            detail.textContent = item.detail;

            element.append(heading, detail);
            steps.append(element);
        });
    };
})();
