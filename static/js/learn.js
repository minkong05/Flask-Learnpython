// -----------------------------
// Logic for adjusting the width of left and right panels
// -----------------------------
(() => {
    const resizer = document.getElementById('resizer');
    const leftPanel = document.querySelector('.left-panel');
    const rightPanel = document.querySelector('.right-panel');
    let isResizing = false;

    resizer.addEventListener('mousedown', (e) => {
        // Start resizing when mouse is pressed down on the divider
        isResizing = true;
        // Temporarily disable text selection and change mouse cursor
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        e.preventDefault(); // Prevent default actions like text selection
    });

    document.addEventListener('mousemove', (e) => {
        if (!isResizing) return;
        const containerWidth = document.querySelector('.main-container').offsetWidth;
        const newLeftWidthPercent = (e.clientX / containerWidth) * 100;

        // Limit minimum to 20% and maximum to 80%
        if (newLeftWidthPercent > 20 && newLeftWidthPercent < 80) {
            leftPanel.style.flex = newLeftWidthPercent;
            rightPanel.style.flex = 100 - newLeftWidthPercent;
        }
    });

    document.addEventListener('mouseup', () => {
        if (isResizing) {
            isResizing = false;
            // Restore text selection and default mouse cursor
            document.body.style.cursor = 'default';
            document.body.style.userSelect = 'auto';

            // Relayout Monaco Editor to fit the new size
            if (window.editor) {
                window.editor.layout();
            }
        }
    });

    // -----------------------------
    // Vertical split (Editor and Terminal) height adjustment logic
    // -----------------------------
    const editorElement = document.getElementById('editor');
    const terminalElement = document.querySelector('.terminal');
    const resizerHorizontal = document.getElementById('resizer-horizontal');

    let isResizingHorizontal = false;

    resizerHorizontal.addEventListener('mousedown', (e) => {
        // Start height adjustment when mouse is pressed on the horizontal divider
        isResizingHorizontal = true;
        document.body.style.cursor = 'row-resize';
        document.body.style.userSelect = 'none';
        e.preventDefault(); // Similarly, only prevent default events on the divider
    });

    document.addEventListener('mousemove', (e) => {
        if (!isResizingHorizontal) return;

        const containerHeight = document.querySelector('.editor-area').offsetHeight;
        const newEditorHeightPercent = (e.clientY / containerHeight) * 100;

        // Limit minimum to 20% and maximum to 80%
        if (newEditorHeightPercent > 20 && newEditorHeightPercent < 95) {
            editorElement.style.flex = `${newEditorHeightPercent}%`;
            terminalElement.style.flex = `${100 - newEditorHeightPercent}%`;
        }
    });

    document.addEventListener('mouseup', () => {
        if (isResizingHorizontal) {
            isResizingHorizontal = false;
            // Restore to normal
            document.body.style.cursor = 'default';
            document.body.style.userSelect = 'auto';

            // Relayout Monaco Editor
            if (window.editor) {
                window.editor.layout();
            }
        }
    });

    document.getElementById('hideButton').addEventListener('click', function () {
        const leftBottom = document.querySelector('.left-bottom');
        const isHidden = leftBottom.classList.toggle('hidden'); // Toggle the 'hidden' class
    
        // Update button text
        this.textContent = isHidden ? 'Show' : 'Hide';
    });

    document.addEventListener("DOMContentLoaded", () => {
        const hideButton = document.getElementById("hideButton");
        const chatContainer = document.querySelector(".chatgpt-container");
        const leftBottom = document.querySelector(".left-bottom");
        
        // Initial state flag
        let isHidden = false;
    
        hideButton.addEventListener("click", () => {
            if (isHidden) {
                // Expand action
                chatContainer.style.display = "flex"; // Restore displayed content
                leftBottom.style.height = "600px"; // Reset height
                hideButton.textContent = "Hide"; // Change button text back
            } else {
                // Collapse action
                chatContainer.style.display = "none"; // Hide content
                leftBottom.style.height = "60px"; // Adjust to show only the header height
                hideButton.textContent = "Show"; // Change button text to "Show"
            }
            isHidden = !isHidden; // Toggle state
        });
    });

})();