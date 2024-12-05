let allCards = []; // Store all fetched cards
let currentPage = 1; // Track the current page for pagination
const limit = 500; // Number of cards to fetch per batch
let debounceTimer;
let isFetching = false; // Prevent multiple simultaneous fetches
let filterSide = ''; // Current side filter
let filterDebateType = ''; // Current Debate Type filter

// Fetch cards from the backend
async function fetchCards(query = '', page = 1) {
    try {
        isFetching = true; // Prevent overlapping fetch requests
        const response = await fetch(`/api/cards?query=${encodeURIComponent(query)}&page=${page}&limit=${limit}`);
        const data = await response.json();

        // Add fetched cards to the master list
        allCards = [...allCards, ...data.cards];

        // Apply filters and render cards
        const filteredCards = filterCards(query, allCards);
        renderCards(filteredCards);

        // Log when all cards are loaded
        if (data.cards.length < limit) {
            console.log("All cards loaded.");
        }

        isFetching = false;
    } catch (error) {
        console.error('Error fetching cards:', error);
        isFetching = false;
    }
}

// Render cards to the DOM
function renderCards(cardsToRender) {
    const cardContainer = document.getElementById('cardContainer');
    cardContainer.innerHTML = ''; // Clear existing cards

    if (!cardsToRender || cardsToRender.length === 0) {
        cardContainer.innerHTML = '<p>No cards found.</p>';
        return;
    }

    cardsToRender.forEach(card => {
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
            <div class="tagline">${card.Tagline || 'No tagline'}</div>
            <div class="citation">${card.Citation || 'No citation'}</div>
            <div class="additional-info">
                <button>${card.Side || 'N/A'}</button>
                <button>${card.Debate_Type || 'N/A'}</button>
                <button>${card.Topic || 'N/A'}</button>
            </div>
            <div class="evidence">${card.Evidence || 'No evidence'}</div>
        `;
        cardContainer.appendChild(cardDiv);
    });
}

// Copy the text of a card
function copyCardText(copyButton) {
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

        const tempContainer = document.createElement('div');
        tempContainer.appendChild(clonedCard);
        tempContainer.style.position = 'absolute';
        tempContainer.style.left = '-9999px'; // Off-screen
        document.body.appendChild(tempContainer);

        const range = document.createRange();
        range.selectNodeContents(tempContainer);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);

        const successful = document.execCommand('copy');
        if (successful) {
            console.log("Card text copied!");
        } else {
            console.error("Copy command failed.");
        }

        document.body.removeChild(tempContainer);
        selection.removeAllRanges();
    } catch (error) {
        console.error("Error copying card:", error);
    }
}

// Apply filters and search
function filterCards(query, allCards) {
    const queryWords = query.toLowerCase().split(/\s+/);

    // Filter by side
    let filteredCards = filterSide
        ? allCards.filter(card => card.Side && card.Side.toLowerCase() === filterSide.toLowerCase())
        : allCards;

    // Filter by debate type
    if (filterDebateType) {
        filteredCards = filteredCards.filter(card =>
            card.Debate_Type && card.Debate_Type.toLowerCase() === filterDebateType.toLowerCase()
        );
    }

    // Apply search query
    if (query) {
        filteredCards = filteredCards.filter(card => {
            const combinedText = `${card.Tagline || ''} ${card.Citation || ''} ${card.Evidence || ''}`.toLowerCase();
            return queryWords.some(word => combinedText.includes(word));
        });
    }

    return filteredCards;
}

// Handle side filtering
function filterBySide(side) {
    filterSide = side; // Update the global filter
    const query = document.getElementById('searchInput').value;
    const filteredCards = filterCards(query, allCards);
    renderCards(filteredCards);
}

// Handle debate type filtering
function filterByDebateType(debateType) {
    filterDebateType = debateType; // Update the global filter
    const query = document.getElementById('searchInput').value;
    const filteredCards = filterCards(query, allCards);
    renderCards(filteredCards);
}

// Debounced search input
function onSearchInputDebounced() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        const query = document.getElementById('searchInput').value;
        const filteredCards = filterCards(query, allCards);
        renderCards(filteredCards);
    }, 300); // 300ms debounce delay
}

// Handle infinite scrolling
function onScroll() {
    const scrollableElement = document.documentElement;

    if (scrollableElement.scrollTop + scrollableElement.clientHeight >= scrollableElement.scrollHeight - 10 && !isFetching) {
        currentPage += 1;
        fetchCards(document.getElementById('searchInput').value, currentPage);
    }
}

// Attach event listeners
window.addEventListener('scroll', onScroll);

// Initialize the page
fetchCards();
