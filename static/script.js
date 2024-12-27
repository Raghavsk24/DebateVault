let page = 1;
let loading = false;
let noMoreData = false; // To indicate no more pages are available


// Debounce function to optimize search input
function debounce(func, delay) {
    let timer;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => func.apply(this, args), delay);
    };
}

async function fetchData() {
    console.log("=== fetchData Called ===");
    if (noMoreData) {
        console.log("No more data to fetch. Exiting fetchData.");
        return; // If no more data available, do not fetch
    }

    const search = document.getElementById('searchInput').value.trim();
    const side = document.getElementById('sideFilter').value;
    const topic = document.getElementById('topicFilter').value;
    const event = document.getElementById('eventFilter').value;

    console.log("Search Input:", search);
    console.log("Side Filter:", side);
    console.log("Topic Filter:", topic);
    console.log("Event Filter:", event);

    // Build URL parameters
    console.log("Building URL parameters");
    const params = new URLSearchParams({
        ...(search && { search }),
        ...(side && { side }),
        ...(topic && { topic }),
        ...(event && { event }),
        page,
        size: 50
    });

    console.log("Query Parameters Sent to Backend:", params.toString());
    console.log("Initiating fetch to backend with URL:", `/data?${params.toString()}`);

    try {
        loading = true;
        document.getElementById('loading').style.display = 'block';
        console.log("Loading indicator displayed.");

        const response = await fetch(`/data?${params}`);
        console.log("Fetch request sent. Awaiting response...");

        if (!response.ok) {
            const errorText = await response.text();
            console.error("Backend Error Response:", errorText);
            alert("Failed to fetch data from backend.");
            loading = false;
            document.getElementById('loading').style.display = 'none';
            console.log("Loading indicator hidden due to error.");
            return;
        }

        const data = await response.json();
        console.log("Data received from backend:", data);

        // Validate response structure
        if (!data || typeof data !== 'object') {
            console.error("Invalid data format received:", data);
            alert("Received invalid data from backend.");
            loading = false;
            document.getElementById('loading').style.display = 'none';
            return;
        }

        // Update the search results count dynamically
        const resultsMessage = document.getElementById("resultsMessage");
        if (data.total === 0 && page === 1) {
            resultsMessage.textContent = "No results found.";
            console.log("No results found for the given filters.");
        } else if (data.total >= 10000) {
            resultsMessage.textContent = "Showing 10,000+ results.";
            console.log("Displaying a message for large result sets.");
        } else {
            resultsMessage.textContent = `Found ${data.total} result${data.total > 1 ? 's' : ''}`;
            console.log(`Found ${data.total} result${data.total > 1 ? 's' : ''}.`);
        }

        console.log("Rendering cards:", data.cards);
        renderCards(data.cards);

        // If fewer cards returned than requested, it means we've hit the end
        if (data.cards.length < 50) {
            noMoreData = true;
            console.log("Fewer cards returned than requested. No more data available.");
        } else {
            console.log("More data available. Ready to fetch next page.");
        }

        loading = false;
        document.getElementById('loading').style.display = 'none';
        console.log("Loading indicator hidden after successful fetch.");

    } catch (err) {
        console.error("Fetch Error:", err);
        alert("Error loading data.");
        loading = false;
        document.getElementById('loading').style.display = 'none';
        console.log("Loading indicator hidden due to fetch error.");
    }
}

// Render cards dynamically
function renderCards(cards) {
    console.log("=== renderCards Called ===", cards);
    const container = document.getElementById('cardContainer');

    // If it's the first page and no cards are found, show message
    if (page === 1 && (!cards || cards.length === 0)) {
        container.innerHTML = '<p>No cards found.</p>';
        console.log("No cards to render for the first page.");
        return;
    }

    // If first page and we have results, clear existing content first
    if (page === 1 && cards.length > 0) {
        container.innerHTML = '';
        console.log("Cleared existing cards for the first page.");
    }

    // If subsequent pages return no cards, do nothing (no clearing)
    if (!cards || cards.length === 0) {
        console.log("No new cards to render for this page.");
        return;
    }

    cards.forEach(card => {
        const cardDiv = document.createElement('div');
        cardDiv.className = 'card';

        cardDiv.innerHTML = `
            <div class="copy-button-container">
                <img 
                    src="https://cdn-icons-png.flaticon.com/128/88/88026.png" 
                    alt="Copy Icon" 
                    class="copy-icon" 
                    onclick="copyCardText(this)" 
                    title="Copy Card"
                />
            </div>
            <div class="tagline">${card.tagline || 'No tagline'}</div>
            <div class="citation">${card.citation || 'No citation'}</div>
            <div class="additional-info">
                <button>${card.side || 'N/A'}</button>
                <button>${card.event || 'N/A'}</button>
                <button>${card.topic || 'N/A'}</button>
            </div>
            <div class="evidence">${card.evidence?.join('<br>') || 'No evidence'}</div>
        `;
        container.appendChild(cardDiv);
        console.log("Rendered card:", card);
    });
}

// Copy the text of a card
function copyCardText(copyButton) {
    console.log("=== copyCardText Called ===");
    try {
        const cardDiv = copyButton.closest('.card');
        if (!cardDiv) {
            console.error("Card element not found.");
            return;
        }

        const clonedCard = cardDiv.cloneNode(true);

        // Remove unnecessary elements
        const buttons = clonedCard.querySelectorAll('.additional-info button, .copy-button-container');
        buttons.forEach(button => button.remove());
        console.log("Cloned card and removed unnecessary elements.");

        const tempContainer = document.createElement('div');
        tempContainer.appendChild(clonedCard);
        tempContainer.style.position = 'absolute';
        tempContainer.style.left = '-9999px'; // Off-screen
        document.body.appendChild(tempContainer);
        console.log("Temporary container created for copying.");

        const range = document.createRange();
        range.selectNodeContents(tempContainer);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        console.log("Selected the content to copy.");

        const successful = document.execCommand('copy');
        if (successful) {
            console.log("Card text copied successfully!");
        } else {
            console.error("Copy command failed.");
        }

        document.body.removeChild(tempContainer);
        selection.removeAllRanges();
        console.log("Cleaned up temporary elements after copying.");
    } catch (error) {
        console.error("Error copying card:", error);
    }
}

// Apply filters
function applyFilters() {
    console.log("=== applyFilters Called ===");
    page = 1;
    noMoreData = false;
    fetchData();
}

// Handle infinite scroll
function handleScroll() {
    if (noMoreData || loading) {
        console.log("Scroll event triggered, but either no more data or currently loading.");
        return;
    }
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 10) {
        console.log("Reached near bottom of the page. Fetching next page.");
        page++;
        fetchData();
    }
}

// Debounced fetchData for search input
const debouncedFetchData = debounce(() => {
    console.log("=== debouncedFetchData Called ===");
    page = 1;
    noMoreData = false;
    fetchData();
}, 300);

// Initial data load
console.log("=== Initial Data Load ===");
fetchData();

// Add the infinite scroll listener
window.addEventListener('scroll', handleScroll);

// Search input with debounce
document.getElementById('searchInput').addEventListener('input', debouncedFetchData);

// Other filters with immediate fetch
document.getElementById('sideFilter').addEventListener('change', applyFilters);
document.getElementById('topicFilter').addEventListener('change', applyFilters);
document.getElementById('eventFilter').addEventListener('change', applyFilters);
