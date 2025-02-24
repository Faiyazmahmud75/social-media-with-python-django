
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


function sharePost(postId) {
    // Placeholder: Replace with proper share functionality
    var dummyInput = document.createElement('input');
    var postUrl = window.location.origin + '/post/' + postId; // adjust URL pattern as needed
    dummyInput.value = postUrl;
    document.body.appendChild(dummyInput);
    dummyInput.select();
    document.execCommand('copy');
    document.body.removeChild(dummyInput);
    alert('Post URL copied to clipboard!');
}