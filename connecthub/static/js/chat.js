document.addEventListener("DOMContentLoaded", function () {
    const chatbox = document.querySelector("#chatbox");
    const wsSchemeChat = window.location.protocol === "https:" ? "wss" : "ws";
    const roomName = JSON.parse(document.getElementById("room_slug").textContent);
    const currentUser = JSON.parse(document.getElementById("current_user").textContent);
    let unreadCounts = {};

    function scrollToBottom() {
        chatbox.scrollTop = chatbox.scrollHeight;
    }
    scrollToBottom();

    function showToast(message) {
        const toastContainer = document.getElementById("toast-container");
        const toast = document.createElement("span");
        toast.className = "toast align-items-center bg-transparent border-0 mb-2 show";
        toast.role = "alert";
        toast.ariaLive = "assertive";
        toast.ariaAtomic = "true";
        toast.setAttribute("data-bs-autohide", "true");
        toast.innerHTML = `
            <div class="d-flex toast-bg">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        toast.addEventListener("hidden.bs.toast", () => {
            toast.remove();
        });
    }

    function updateUnreadCounts(data) {
        data.unread_per_chat.forEach(item => {
            unreadCounts[item.username] = item.unread_count;
        });
        updateBadges();
        updateNavbarBadge();
    }

    function updateBadges() {
        const currentUser = JSON.parse(document.getElementById("current_user").textContent);
        document.querySelectorAll('.list-group-item').forEach(chatItem => {
            const username = chatItem.getAttribute('data-id');
            const badge = chatItem.querySelector('.unread-badge');
            if (unreadCounts[username] > 0) {
                if (badge) {
                    badge.textContent = unreadCounts[username];
                } else {
                    const newBadge = document.createElement("span");
                    newBadge.className = "badge rounded-pill unread-badge";
                    newBadge.textContent = unreadCounts[username];
                    chatItem.querySelector('.d-flex.justify-content-between').appendChild(newBadge);
                }
            } else if (badge) {
                badge.remove();
            }
        });
    }

    function updateNavbarBadge() {
        const navbarBadge = document.querySelector("#chat-count");
        const totalUnreadConversations = Object.values(unreadCounts).filter(count => count > 0).length;
        if (navbarBadge) {
            if (totalUnreadConversations > 0) {
                navbarBadge.style.display = "inline";
                navbarBadge.textContent = totalUnreadConversations;
            } else {
                navbarBadge.style.display = "none";
            }
        }
    }

    document.querySelectorAll('.list-group-item').forEach(chatItem => {
        chatItem.addEventListener('click', () => {
            const username = chatItem.getAttribute('data-id');
            unreadCounts[username] = 0;
            updateBadges();
            updateNavbarBadge();
        });
    });

    if (roomName) {
        const chatSocket = new WebSocket(`${wsSchemeChat}://${window.location.host}/ws/chat/${roomName}/`);

        chatSocket.onopen = function () {
            console.log("The connection was set up successfully!");
            chatSocket.send(JSON.stringify({ type: "message_read", sender: roomName }));

            // Store the roomName in localStorage.
            let openedConversations = JSON.parse(localStorage.getItem('openedConversations')) || [];
            if (!openedConversations.includes(roomName)) {
                openedConversations.push(roomName);
                localStorage.setItem('openedConversations', JSON.stringify(openedConversations));
            }
        };

        chatSocket.onclose = function (e) {
            console.error(`WebSocket closed unexpectedly: Code=${e.code}, Reason=${e.reason}`);

            // Remove the roomName from localStorage.
            let openedConversations = JSON.parse(localStorage.getItem('openedConversations')) || [];
            openedConversations = openedConversations.filter(item => item !== roomName);
            localStorage.setItem('openedConversations', JSON.stringify(openedConversations));
        };

        document.querySelector("#my_input").focus();
        document.querySelector("#my_input").onkeyup = function (e) {
            if (e.keyCode === 13) {
                e.preventDefault();
                document.querySelector("#submit_button").click();
            }
        };

        document.querySelector("#submit_button").onclick = function () {
            const messageInput = document.querySelector("#my_input");
            const message = messageInput.value.trim();

            if (message !== "") {
                chatSocket.send(JSON.stringify({ type: "message", message: message }));
                messageInput.value = "";
            } else {
                showToast("Cannot send an empty message");
            }
        };

        chatSocket.onmessage = function (e) {
            const data = JSON.parse(e.data);

            if (data.message && data.sender) {
                const chatbox = document.querySelector("#chatbox");
                const noMessages = document.querySelector(".no-messages");

                if (noMessages) {
                    noMessages.style.display = "none";
                }

                const div = document.createElement("div");
                div.className = "chat-message " + (data.sender === currentUser ? "sender" : "receiver");
                div.innerHTML = `<span>${data.message}</span>`;
                chatbox.appendChild(div);

                scrollToBottom();

                const chatItem = document.querySelector(`.list-group-item[data-id="${data.sender}"]`);
                if (chatItem) {
                    const lastMessage = chatItem.querySelector("#last-message");
                    const timestamp = chatItem.querySelector("small.timestamp");

                    if (lastMessage) {
                        lastMessage.innerHTML = (data.sender === currentUser ? "You: " : "") + data.message;
                    }

                    if (timestamp) {
                        timestamp.innerHTML = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
                    }
                    const contacts = document.querySelector(".contacts");
                    contacts.prepend(chatItem);
                }
            } else if (data.type !== "update_unread_counts") { // only log if it is not update_unread_counts.
                console.error("Message or sender data is missing. Data received:", JSON.stringify(data, null, 2));
            }
        };
    }

    const chatSocketGlobal = new WebSocket(`${wsSchemeChat}://${window.location.host}/ws/chat/global/`);

    chatSocketGlobal.onmessage = function (e) {
        const data = JSON.parse(e.data);
        if (data.type === "update_unread_counts") {
            updateUnreadCounts(data);
        }
    };

    function updateUnreadCounts(data) {
        const navbarBadge = document.querySelector("#chat-count");
        if (navbarBadge) {
            if (data.unread_conversations > 0) {
                navbarBadge.style.display = "inline";
                navbarBadge.textContent = data.unread_conversations;
            } else {
                navbarBadge.style.display = "none";
            }
        }
    
        data.unread_per_chat.forEach(item => {
            const sidebarBadge = document.querySelector(`#badge-${item.username}`);
            if (sidebarBadge) {
                if (item.unread_count > 0) {
                    sidebarBadge.textContent = item.unread_count;
                } else {
                    sidebarBadge.remove();
                }
            } else if (item.unread_count > 0) {
                const chatItem = document.querySelector(`.list-group-item[data-id="${item.username}"]`);
                if (chatItem) {
                    const badge = document.createElement("span");
                    badge.className = "badge rounded-pill unread-badge";
                    badge.id = `badge-${item.username}`;
                    badge.textContent = item.unread_count;
                    chatItem.querySelector('.d-flex.justify-content-between').appendChild(badge);
                }
            }
        });
    }

    updateUnreadCounts(JSON.parse(document.getElementById('unread_counts').textContent));
});