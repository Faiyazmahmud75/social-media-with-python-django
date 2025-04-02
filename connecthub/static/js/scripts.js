
// text toggler
function toggleText(postId) {
    var textElement = document.getElementById('post-text-' + postId);
    var toggleLink = document.getElementById('toggle-link-' + postId);
    var fullText = textElement.getAttribute('data-full');
    var truncatedText = textElement.getAttribute('data-truncated');

    if (toggleLink.innerHTML.trim() === "see more") {
        textElement.innerHTML = fullText + ' <a href="#" onclick="toggleText(' + postId + '); return false;" id="toggle-link-' + postId + '">see less</a>';
    } else {
        textElement.innerHTML = truncatedText + '... <a href="#" onclick="toggleText(' + postId + '); return false;" id="toggle-link-' + postId + '">see more</a>';
    }
}

// search bar 
 function toggleSearch() {
    const searchBar = document.querySelector('.search-bar-container');
    const searchInput = document.querySelector('.search-input');

    if (!searchBar.classList.contains('active')) {
      searchBar.classList.add('active');
      searchInput.focus();
    }
  }

  function enableSubmit() {
    const searchButton = document.querySelector('.search-button');
    searchButton.setAttribute('type', 'submit'); // Change to submit only when input is typed
  }

  // Close search bar when clicking outside
  document.addEventListener('click', function(event) {
    const searchBar = document.querySelector('.search-bar-container');
    const searchInput = document.querySelector('.search-input');
    const searchButton = document.querySelector('.search-button');

    if (!searchBar.contains(event.target)) {
      searchBar.classList.remove('active');
      searchButton.setAttribute('type', 'button'); // Reset to button when collapsed
      searchInput.value = ""; 
    }
  });

// Post link share   
function sharePost(postId) {
    var dummyInput = document.createElement('input');
    var postUrl = window.location.origin + '/post/' + postId;
    dummyInput.value = postUrl;
    document.body.appendChild(dummyInput);
    dummyInput.select();
    document.execCommand('copy');
    document.body.removeChild(dummyInput);
    alert('Post URL copied to clipboard!');
}

// Initialize Swiper
var swiper = new Swiper('.swiper', {
    slidesPerView: 1,
    spaceBetween: 10,
    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    },
    pagination: {
        el: '.swiper-pagination',
        clickable: true,
    },
    lazy: true,
    zoom: true,
});

// Media removal
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".remove-media").forEach(button => {
        button.addEventListener("click", function () {
            let mediaId = this.getAttribute("data-media-id");
            let mediaElement = document.getElementById("media-" + mediaId);
            
            // Hide media element from UI
            mediaElement.style.display = "none";

            // Remove the corresponding hidden input field
            let hiddenInput = mediaElement.querySelector("input[name='keep_media']");
            if (hiddenInput) {
                hiddenInput.remove();
            }
        });
    });
});

// Page loader
document.addEventListener("DOMContentLoaded", function () {
    setTimeout(() => {
        document.getElementById("page-loader").style.display = "none";
    }, 100); // Add a slight delay for smooth hiding
});


// Footer bottomed
document.addEventListener("DOMContentLoaded", function () {
    let bodyHeight = document.body.scrollHeight;
    let windowHeight = window.innerHeight;
    console.log('bodyhight: ', bodyHeight, 'window: ',windowHeight)
    let footer = document.querySelector("footer");

    if (bodyHeight < windowHeight) {
        this.body.style.minHeight = "100vh"
        footer.style.position = "absolute";
        footer.style.bottom = "0";
        footer.style.width = "100%";
    } else {
        footer.style.position = "static";
    }
});

// Comment edit toggle
function toggleEdit(commentId) {
    var text = document.getElementById("comment-text-" + commentId);
    var form = document.getElementById("edit-form-" + commentId);
    
    if (form.style.display === "none") {
        form.style.display = "flex";
        text.style.display = "none";
    } else {
        form.style.display = "none";
        text.style.display = "block";
    }
}



window.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";

// WebSocket setup for notications
const socket = new WebSocket(`${wsScheme}://${window.location.host}/ws/notifications/`);

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    
    if (data.type === 'connection_established' || !data.content) {
        console.log("Received system message:", data);
        return;
    }

    fetchUnreadCount();

    let notificationList = document.getElementById("notification-list");
    let notificationContainer = document.getElementById("notification-container");

    if (!notificationList) {
        notificationList = document.createElement("ul");
        notificationList.id = "notification-list";
        notificationContainer.innerHTML = `<p class="text-muted text-center">No notifications</p>`;
        notificationContainer.appendChild(notificationList);
    }

    // **Event Badge Mapping**
    const eventIcons = {
        "like": "👍",  
        "comment": "💬",
        "friend_request": "🤝",
        "freind_accepted": "✅",
        "mention": "📢"
    };

    let newNotification = document.createElement("li");
    newNotification.className = "notification-card unread";
    newNotification.dataset.id = data.notification_id || "new";

    let link = document.createElement("a");
    link.href = data.url || '#';
    link.className = "notification-link";
    link.dataset.id = data.notification_id || "new";
    
    link.innerHTML = `
        <div class="notification-card-body d-flex align-items-center">
            <img src="${data.sender_image}" class="rounded-circle me-2" width="40" height="40" alt="User Image">
            <div>
                <h5 class="notification-title">${data.content}</h5>
                <p class="notification-info">${data.created_at}</p>
            </div>
            <span class="badge">${eventIcons[data.event_type] || "🔔"}</span>
        </div>
    `;
    
    newNotification.appendChild(link);
    notificationList.insertBefore(newNotification, notificationList.firstChild);
};

// Fetch unread notifications count
function fetchUnreadCount() {
    fetch('/notifications/unread-count/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            updateNotificationCount(data.unread_count);
        })
        .catch(error => console.error("Error fetching unread count:", error));
}

// Update unread notification count in UI
function updateNotificationCount(unreadCount) {
    const countElement = document.getElementById('notification-count');

    if (!countElement) return;

    if (unreadCount > 0) {
        countElement.innerText = unreadCount;
        countElement.style.display = 'inline-block'; 
    } else {
        countElement.style.display = 'none';
    }
}

// Mark individual notification as read
document.addEventListener('click', function(e) {
    const link = e.target.closest('.notification-link');
    if (link) {
        const notificationId = link.dataset.id;

        // Instantly update UI
        const badge = link.querySelector('.badge');
        if (badge) badge.remove();
        link.closest('.notification-card').classList.remove('unread');

        fetchUnreadCount();

        // Send request to mark as read in the database
        if (notificationId && notificationId !== "new") {
            fetch(`/notifications/mark-read/${notificationId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': window.csrfToken,  
                    'Content-Type': 'application/json'
                }
            }).then(response => response.json())
            .then(data => console.log("Marked as read:", data));
        }
    }
});

// Mark all as read
document.addEventListener('DOMContentLoaded', function() {
    const markAllReadBtn = document.getElementById('mark-all-read');

    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', function() {
            // updating the UI first 😆
            const unreadCards = document.querySelectorAll('.notification-card.unread');

            unreadCards.forEach(card => {
                card.classList.remove('unread');
                const badge = card.querySelector('.badge');
                if (badge) badge.remove();
            });
            
            updateNotificationCount(0); 

            // Send request to backend
            fetch('/notifications/mark-all-read/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': window.csrfToken,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.querySelectorAll('.notification-card.unread').forEach(card => {
                        card.classList.remove('unread');
                        const badge = card.querySelector('.badge');
                        if (badge) badge.remove();
                    });

                    fetchUnreadCount();
                }
            })
            .catch(error => console.error("Error marking all as read:", error));
        });
    }
});



// Clear all notifications
document.addEventListener('DOMContentLoaded', function() {
    const clearAllBtn = document.getElementById('clear-all');
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to clear all notifications?')) {
                fetch('/notifications/clear-all/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': window.csrfToken,
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('notification-container').innerHTML = `
                        <div class="alert alert-light text-center p-4" role="alert">
                            <i class="bi bi-bell-slash" style="font-size: 2rem;"></i> No new notifications
                        </div>
                    `;
                    fetchUnreadCount();
                });
            }
        });
    }
});

// Initialize unread count on page load
document.addEventListener('DOMContentLoaded', function () {
    fetchUnreadCount();
});

