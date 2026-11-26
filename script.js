const chat = document.getElementById("chat");
const input = document.getElementById("message");
const sendBtn = document.getElementById("sendBtn");
const counter = document.getElementById("counter");

let history = [];

input.addEventListener("input", () => {
    counter.textContent = `${input.value.length} / 8000`;
});

function addMessage(text, type) {
    const bubble = document.createElement("div");
    bubble.className = `message ${type}`;

    // textContent prevents HTML in messages from being executed.
    bubble.textContent = text;

    chat.appendChild(bubble);
    chat.scrollTop = chat.scrollHeight;
    return bubble;
}

async function sendMessage() {
    const message = input.value.trim();

    if (!message) {
        input.focus();
        return;
    }

    addMessage(message, "user");
    input.value = "";
    counter.textContent = "0 / 8000";
    sendBtn.disabled = true;
    sendBtn.textContent = "Thinking... 🤔";

    const loading = addMessage(
        "Friend, oka second... explain chestunna 😊",
        "bot"
    );

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                history: history
            })
        });

        const data = await response.json();
        loading.textContent = data.reply || "Friend, response raledu.";

        if (response.ok) {
            history.push(
                { role: "user", content: message },
                { role: "assistant", content: data.reply }
            );

            // Keep recent conversation only.
            history = history.slice(-10);
        }
    } catch (error) {
        loading.textContent =
            "Friend, server connect avvaledu. " +
            "Python server running lo undo check cheyyi.";
    } finally {
        sendBtn.disabled = false;
        sendBtn.textContent = "Explain to me ✨";
        input.focus();
        chat.scrollTop = chat.scrollHeight;
    }
}

sendBtn.addEventListener("click", sendMessage);

input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
        event.preventDefault();
        sendMessage();
    }
});