const uploadModeButton =
    document.getElementById("uploadModeButton");

const cameraModeButton =
    document.getElementById("cameraModeButton");

const uploadView =
    document.getElementById("uploadView");

const cameraView =
    document.getElementById("cameraView");

const dropZone =
    document.getElementById("dropZone");

const browseButton =
    document.getElementById("browseButton");

const uploadActionButton =
    document.getElementById("uploadActionButton");

const fileInput =
    document.getElementById("fileInput");

const previewContainer =
    document.getElementById("previewContainer");

const pcbPreview =
    document.getElementById("pcbPreview");

const inspectButton =
    document.getElementById("inspectButton");

const captureButton =
    document.getElementById("captureButton");

const liveInspectionButton =
    document.getElementById("liveInspectionButton");


let currentMode = "upload";
let selectedFile = null;


/* ========================================
   MODE SWITCHING
======================================== */

function setMode(mode) {
    currentMode = mode;

    const uploadActive =
        mode === "upload";

    uploadModeButton.classList.toggle(
        "active",
        uploadActive
    );

    cameraModeButton.classList.toggle(
        "active",
        !uploadActive
    );

    uploadView.classList.toggle(
        "active",
        uploadActive
    );

    cameraView.classList.toggle(
        "active",
        !uploadActive
    );

    if (uploadActive) {
        captureButton.disabled = true;
        liveInspectionButton.disabled = true;

        if (selectedFile) {
            previewContainer.classList.remove(
                "hidden"
            );

            inspectButton.disabled = false;
        } else {
            previewContainer.classList.add(
                "hidden"
            );

            inspectButton.disabled = true;
        }

    } else {
        previewContainer.classList.add(
            "hidden"
        );

        inspectButton.disabled = true;

        /*
         * Camera controls remain disabled for now.
         * They will be enabled once the Jetson camera
         * backend is connected.
         */
        captureButton.disabled = true;
        liveInspectionButton.disabled = true;
    }
}


uploadModeButton.addEventListener(
    "click",
    () => setMode("upload")
);


cameraModeButton.addEventListener(
    "click",
    () => setMode("camera")
);


/* ========================================
   FILE SELECTION
======================================== */

function openFilePicker() {
    fileInput.click();
}


browseButton.addEventListener(
    "click",
    openFilePicker
);


uploadActionButton.addEventListener(
    "click",
    () => {
        setMode("upload");
        openFilePicker();
    }
);


fileInput.addEventListener(
    "change",
    (event) => {
        const file =
            event.target.files[0];

        if (file) {
            loadSelectedFile(file);
        }
    }
);


/* ========================================
   DRAG AND DROP
======================================== */

dropZone.addEventListener(
    "dragover",
    (event) => {
        event.preventDefault();

        dropZone.classList.add(
            "drag-active"
        );
    }
);


dropZone.addEventListener(
    "dragleave",
    () => {
        dropZone.classList.remove(
            "drag-active"
        );
    }
);


dropZone.addEventListener(
    "drop",
    (event) => {
        event.preventDefault();

        dropZone.classList.remove(
            "drag-active"
        );

        const file =
            event.dataTransfer.files[0];

        if (file) {
            loadSelectedFile(file);
        }
    }
);


/* ========================================
   IMAGE PREVIEW
======================================== */

function loadSelectedFile(file) {
    const allowedTypes = [
        "image/jpeg",
        "image/png",
        "image/bmp"
    ];

    if (!allowedTypes.includes(file.type)) {
        alert(
            "Please select a JPG, JPEG, PNG, or BMP image."
        );

        return;
    }

    selectedFile = file;

    const reader =
        new FileReader();

    reader.onload = (event) => {
        pcbPreview.src =
            event.target.result;

        previewContainer.classList.remove(
            "hidden"
        );

        inspectButton.disabled = false;
    };

    reader.readAsDataURL(file);
}


/* ========================================
   INITIAL STATE
======================================== */

setMode("upload");

/* ========================================
   API HEALTH
======================================== */

const apiStatus =
    document.getElementById("apiStatus");

const inspectionBadge =
    document.getElementById("inspectionBadge");

const resultEmptyState =
    document.getElementById("resultEmptyState");

const resultContent =
    document.getElementById("resultContent");

const defectCount =
    document.getElementById("defectCount");

const detectionsList =
    document.getElementById("detectionsList");

const decisionReason =
    document.getElementById("decisionReason");

const pipelineLatency =
    document.getElementById("pipelineLatency");

const detectionCanvas =
    document.getElementById("detectionCanvas");


async function checkApiHealth() {
    try {
        const response =
            await fetch("/health");

        if (!response.ok) {
            throw new Error(
                "Health endpoint returned an error."
            );
        }

        const data =
            await response.json();

        if (
            data.status === "ok" &&
            data.model_loaded === true
        ) {
            apiStatus.textContent =
                "Online";

            apiStatus.classList.remove(
                "offline"
            );

            apiStatus.classList.add(
                "online"
            );
        } else {
            throw new Error(
                "Model is not ready."
            );
        }

    } catch (error) {
        apiStatus.textContent =
            "Offline";

        apiStatus.classList.remove(
            "online"
        );

        apiStatus.classList.add(
            "offline"
        );
    }
}


/* ========================================
   PCB INSPECTION
======================================== */

inspectButton.addEventListener(
    "click",
    inspectSelectedPCB
);


async function inspectSelectedPCB() {
    if (!selectedFile) {
        return;
    }

    setInspectionLoading(true);

    clearDetectionCanvas();

    const formData =
        new FormData();

    formData.append(
        "file",
        selectedFile
    );

    try {
        const response =
            await fetch(
                "/inspect",
                {
                    method: "POST",
                    body: formData
                }
            );

        if (!response.ok) {
            let message =
                "Inspection failed.";

            try {
                const errorData =
                    await response.json();

                if (errorData.detail) {
                    message =
                        errorData.detail;
                }
            } catch {
                // Keep default message.
            }

            throw new Error(message);
        }

        const result =
            await response.json();

        displayInspectionResult(result);

    } catch (error) {
        displayInspectionError(
            error.message
        );

    } finally {
        setInspectionLoading(false);
    }
}


/* ========================================
   LOADING STATE
======================================== */

function setInspectionLoading(isLoading) {
    if (isLoading) {
        inspectButton.disabled = true;

        inspectButton.textContent =
            "Inspecting…";

        inspectionBadge.textContent =
            "RUNNING";

        inspectionBadge.className =
            "result-badge idle";

    } else {
        inspectButton.disabled =
            !selectedFile;

        inspectButton.textContent =
            "Inspect PCB";
    }
}


/* ========================================
   DISPLAY RESULT
======================================== */

function displayInspectionResult(result) {
    resultEmptyState.classList.add(
        "hidden"
    );

    resultContent.classList.remove(
        "hidden"
    );

    const status =
        String(result.status).toUpperCase();

    inspectionBadge.textContent =
        status;

    inspectionBadge.className =
        "result-badge";

    if (status === "FAIL") {
        inspectionBadge.classList.add(
            "fail"
        );

    } else if (
        status === "UNCERTAIN"
    ) {
        inspectionBadge.classList.add(
            "uncertain"
        );

    } else if (
        status === "PASS"
    ) {
        inspectionBadge.classList.add(
            "pass"
        );

    } else {
        inspectionBadge.classList.add(
            "idle"
        );
    }


    defectCount.textContent =
        result.defect_count;


    decisionReason.textContent =
        result.reason;


    pipelineLatency.textContent =
        `${result.inference_pipeline_ms.toFixed(2)} ms`;


    renderDetections(
        result.detections
    );


    drawDetections(
        result.detections,
        result.image_width,
        result.image_height
    );
}


/* ========================================
   DETECTION LIST
======================================== */

function renderDetections(detections) {
    detectionsList.innerHTML = "";

    if (!detections.length) {
        const emptyMessage =
            document.createElement("div");

        emptyMessage.className =
            "detection-item";

        emptyMessage.innerHTML = `
            <span class="detection-name">
                No qualifying detections
            </span>
        `;

        detectionsList.appendChild(
            emptyMessage
        );

        return;
    }


    detections.forEach(
        (detection, index) => {
            const item =
                document.createElement("div");

            item.className =
                "detection-item";

            const confidence =
                (
                    detection.confidence *
                    100
                ).toFixed(1);

            item.innerHTML = `
                <span class="detection-name">
                    ${index + 1}.
                    ${formatClassName(
                        detection.class_name
                    )}
                </span>

                <span class="detection-confidence">
                    ${confidence}%
                </span>
            `;

            detectionsList.appendChild(
                item
            );
        }
    );
}


function formatClassName(name) {
    return name
        .replaceAll("_", " ")
        .replace(
            /\b\w/g,
            character =>
                character.toUpperCase()
        );
}


/* ========================================
   DRAW BOUNDING BOXES
======================================== */

function drawDetections(
    detections,
    sourceWidth,
    sourceHeight
) {
    if (!pcbPreview.complete) {
        pcbPreview.onload = () => {
            drawDetections(
                detections,
                sourceWidth,
                sourceHeight
            );
        };

        return;
    }


    const containerRect =
        previewContainer
            .getBoundingClientRect();


    const containerWidth =
        containerRect.width;

    const containerHeight =
        containerRect.height;


    detectionCanvas.width =
        containerWidth;

    detectionCanvas.height =
        containerHeight;


    const context =
        detectionCanvas.getContext(
            "2d"
        );


    context.clearRect(
        0,
        0,
        containerWidth,
        containerHeight
    );


    /*
     * The image uses object-fit: contain.
     * Calculate its actual displayed size
     * inside the preview area.
     */

    const imageAspect =
        sourceWidth /
        sourceHeight;

    const containerAspect =
        containerWidth /
        containerHeight;


    let displayedWidth;
    let displayedHeight;


    if (
        imageAspect >
        containerAspect
    ) {
        displayedWidth =
            containerWidth;

        displayedHeight =
            containerWidth /
            imageAspect;

    } else {
        displayedHeight =
            containerHeight;

        displayedWidth =
            containerHeight *
            imageAspect;
    }


    const offsetX =
        (
            containerWidth -
            displayedWidth
        ) / 2;

    const offsetY =
        (
            containerHeight -
            displayedHeight
        ) / 2;


    const scaleX =
        displayedWidth /
        sourceWidth;

    const scaleY =
        displayedHeight /
        sourceHeight;


    detections.forEach(
        detection => {
            const [
                x1,
                y1,
                x2,
                y2
            ] = detection.bbox;


            const boxX =
                offsetX +
                x1 * scaleX;

            const boxY =
                offsetY +
                y1 * scaleY;

            const boxWidth =
                (x2 - x1) *
                scaleX;

            const boxHeight =
                (y2 - y1) *
                scaleY;


            context.lineWidth = 3;

            context.strokeStyle =
                "#ff4d5a";

            context.fillStyle =
                "#ff4d5a";


            context.strokeRect(
                boxX,
                boxY,
                boxWidth,
                boxHeight
            );


            const confidence =
                (
                    detection.confidence *
                    100
                ).toFixed(1);


            const label =
                `${formatClassName(
                    detection.class_name
                )} ${confidence}%`;


            context.font =
                "bold 14px system-ui";


            const textWidth =
                context.measureText(
                    label
                ).width;


            const labelHeight = 26;


            let labelY =
                boxY - labelHeight;

            if (labelY < 0) {
                labelY =
                    boxY;
            }


            context.fillRect(
                boxX,
                labelY,
                textWidth + 16,
                labelHeight
            );


            context.fillStyle =
                "#ffffff";

            context.fillText(
                label,
                boxX + 8,
                labelY + 18
            );
        }
    );
}


function clearDetectionCanvas() {
    const context =
        detectionCanvas.getContext(
            "2d"
        );

    context.clearRect(
        0,
        0,
        detectionCanvas.width,
        detectionCanvas.height
    );
}


/* ========================================
   ERROR DISPLAY
======================================== */

function displayInspectionError(message) {
    resultEmptyState.classList.add(
        "hidden"
    );

    resultContent.classList.remove(
        "hidden"
    );

    inspectionBadge.textContent =
        "ERROR";

    inspectionBadge.className =
        "result-badge fail";

    defectCount.textContent =
        "—";

    detectionsList.innerHTML = "";

    decisionReason.textContent =
        message;

    pipelineLatency.textContent =
        "—";
}


/* ========================================
   WINDOW RESIZE
======================================== */

window.addEventListener(
    "resize",
    () => {
        clearDetectionCanvas();
    }
);


/* ========================================
   INITIAL API CHECK
======================================== */

checkApiHealth();