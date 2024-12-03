let allCards = []; // Store all fetched cards
let currentPage = 1; // Track current page
const limit = 100; // Number of cards to fetch per batch
let debounceTimer;
let isFetching = false; // Prevent multiple fetches during scroll
let filterSide = ''; // Current side filter (empty means no filter)

// Fetch cards from the backend
async function fetchCards(query = '', page = 1) {
    try {
        isFetching = true;
        const response = await fetch(`/api/cards?query=${encodeURIComponent(query)}&page=${page}&limit=${limit}`);
        const data = await response.json();

        // Add new cards to the master list
        allCards = [...allCards, ...data.cards];

        // Render the initial list of cards if query is empty
        if (!query && !filterSide) {
            renderCards(allCards);
        } else {
            const filteredCards = filterCards(query, allCards);
            renderCards(filteredCards);
        }

        // Check if we have reached the total
        if (data.cards.length < limit) {
            console.log("All cards loaded.");
        }

        isFetching = false; // Reset fetching state
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

function copyCardText(copyButton) {
    try {
        // Find the parent card div
        const cardDiv = copyButton.closest('.card');
        if (!cardDiv) {
            console.error("Card element not found.");
            return;
        }

        // Clone the card to isolate modifications
        const clonedCard = cardDiv.cloneNode(true);

        // Remove unnecessary elements (e.g., buttons and copy button container)
        const buttons = clonedCard.querySelectorAll('.additional-info button, .copy-button-container');
        buttons.forEach(button => button.remove());

        // Adjust styles for the remaining text content
        const tagline = clonedCard.querySelector('.tagline');
        const citation = clonedCard.querySelector('.citation');
        const evidence = clonedCard.querySelector('.evidence');

        if (tagline) tagline.style.fontSize = '12pt';
        if (tagline) tagline.style.fontWeight = 'bold';
        if (citation) citation.style.fontSize = '7pt';
        if (citation) citation.style.color = 'black';
        if (evidence) evidence.style.fontSize = '7pt';
        if (evidence) evidence.style.color = 'black';

        // Use a temporary container to enable rich-text copying
        const tempContainer = document.createElement('div');
        tempContainer.appendChild(clonedCard);
        tempContainer.style.position = 'absolute';
        tempContainer.style.left = '-9999px'; // Off-screen
        document.body.appendChild(tempContainer);

        // Create a Range and Selection to copy HTML content
        const range = document.createRange();
        range.selectNodeContents(tempContainer);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);

        // Execute the copy command
        const successful = document.execCommand('copy');
        if (successful) {
        } else {
        }

        // Cleanup
        document.body.removeChild(tempContainer);
        selection.removeAllRanges();
    } catch (error) {
        console.error("An error occurred while copying the card:", error);
    }
}

// Filter cards with fuzzy matching, spelling correction, and exact match prioritization
function filterCards(query, allCards) {
    const queryWords = query.toLowerCase().split(/\s+/); // Split query into individual terms
    const similarityThreshold = 70; // Minimum similarity percentage for a match

    // Weights for different fields
    const weights = {
        exactMatch: 10, // Highest priority for exact matches
        tagline: 5,
        styledEvidence: 4,
        citation: 3,
        plainEvidence: 2,
    };

    // Apply side filtering first
    const sideFilteredCards = filterSide
        ? allCards.filter(card => card.Side && card.Side.toLowerCase() === filterSide.toLowerCase())
        : allCards;

    // Rank cards based on fuzzy matching and exact match prioritization
    const rankedCards = sideFilteredCards.map(card => {
        const tagline = card.Tagline ? card.Tagline.toLowerCase() : '';
        const citation = card.Citation ? card.Citation.toLowerCase() : '';
        const evidence = card.Evidence ? card.Evidence.toLowerCase() : '';
        
        // Styled evidence is identified by markers like bold, underline, or highlight
        const styledEvidence = evidence.match(/<b>|<u>|<mark>/) ? evidence : '';

        let relevanceScore = 0;
        let matchesInTagline = 0;
        let matchesInStyledEvidence = 0;
        let matchesInCitation = 0;
        let matchesInPlainEvidence = 0;

        // Check for exact match in any field
        const combinedText = `${tagline} ${citation} ${evidence}`;
        if (combinedText.includes(query.toLowerCase())) {
            relevanceScore += weights.exactMatch; // Boost score for exact matches
        }

        // Calculate scores and count matches in each section
        queryWords.forEach(word => {
            // Check tagline
            if (tagline.includes(word)) {
                relevanceScore += weights.tagline;
                matchesInTagline++;
            }
            // Check styled evidence
            if (styledEvidence.includes(word)) {
                relevanceScore += weights.styledEvidence;
                matchesInStyledEvidence++;
            }
            // Check citation
            if (citation.includes(word)) {
                relevanceScore += weights.citation;
                matchesInCitation++;
            }
            // Check plain evidence
            if (evidence.includes(word)) {
                relevanceScore += weights.plainEvidence;
                matchesInPlainEvidence++;
            }
        });

        // Exclude cards with only one or two matches in plain evidence
        const totalMatches = matchesInTagline + matchesInStyledEvidence + matchesInCitation + matchesInPlainEvidence;
        if (totalMatches <= 2 && matchesInPlainEvidence === totalMatches) {
            relevanceScore = 0; // Exclude card by setting relevance score to 0
        }

        return { card, relevanceScore };
    });

    // Filter and sort cards by relevance score
    const filteredCards = rankedCards
        .filter(item => item.relevanceScore > 0) // Include only relevant cards
        .sort((a, b) => b.relevanceScore - a.relevanceScore) // Sort by relevance
        .map(item => item.card); // Extract only the card data

    // Debugging Log
    console.log('Filtered Cards with Exact Match Priority:', filteredCards);

    return filteredCards;
}

// Function to handle side filtering
function filterBySide(side) {
    filterSide = side; // Update the global filterSide variable
    const query = document.getElementById('searchInput').value; // Get the current search query
    const filteredCards = filterCards(query, allCards); // Apply search and side filters
    renderCards(filteredCards); // Render the filtered cards
}

function levenshteinDistance(a, b) {
    const matrix = Array.from({ length: a.length + 1 }, () => Array(b.length + 1).fill(0));

    for (let i = 0; i <= a.length; i++) matrix[i][0] = i;
    for (let j = 0; j <= b.length; j++) matrix[0][j] = j;

    for (let i = 1; i <= a.length; i++) {
        for (let j = 1; j <= b.length; j++) {
            matrix[i][j] = Math.min(
                matrix[i - 1][j] + 1,
                matrix[i][j - 1] + 1,
                matrix[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1)
            );
        }
    }

    return matrix[a.length][b.length];
}

function similarityScore(a, b) {
    const maxLength = Math.max(a.length, b.length);
    return (1 - levenshteinDistance(a, b) / maxLength) * 100; // Return as a percentage
}


// Function to handle side filtering
function filterBySide(side) {
    filterSide = side; // Update the global filterSide variable
    const query = document.getElementById('searchInput').value; // Get the current search query
    const filteredCards = filterCards(query, allCards); // Apply search and side filters
    renderCards(filteredCards); // Render the filtered cards
}



// Handle filtering by side
function filterBySide(side) {
    filterSide = side; // Update the filterSide variable
    const filteredCards = filterCards(document.getElementById('searchInput').value, allCards); // Apply the side filter
    renderCards(filteredCards); // Render filtered cards
}

// Handle infinite scrolling
function onScroll() {
    const scrollableElement = document.documentElement;

    // Check if the user has scrolled near the bottom of the page
    const scrollTop = scrollableElement.scrollTop;
    const scrollHeight = scrollableElement.scrollHeight;
    const clientHeight = scrollableElement.clientHeight;

    if (scrollTop + clientHeight >= scrollHeight - 10 && !isFetching) {
        currentPage += 1; // Increment the page number
        fetchCards(document.getElementById('searchInput').value, currentPage); // Fetch the next set of cards
    }
}

// Debounced search input
function onSearchInputDebounced() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        const filteredCards = filterCards(document.getElementById('searchInput').value, allCards); // Apply the search filter
        renderCards(filteredCards);
    }, 300); // 150ms debounce delay
}

// Attach the scroll event listener
window.addEventListener('scroll', onScroll);

// Initialize the page
fetchCards(); // Fetch the initial set of cards
