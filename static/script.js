let page = 1;
        let loading = false;
        let noMoreData = false; // To indicate no more pages are available

        const topics = {
            "PF": ["Sep/Oct 24", "Nov/Dec 24", "Jan 24"],
            "LD": ["Sep/Oct 24", "Nov/Dec 24", "Jan/Feb 24"],
            "CX": ["2024"]
        };

        // Debounce function to optimize search input
        function debounce(func, delay) {
            let timer;
            return function (...args) {
                clearTimeout(timer);
                timer = setTimeout(() => func.apply(this, args), delay);
            };
        }

        async function fetchData() {
            if (noMoreData) return; // If no more data available, do not fetch

            const search = document.getElementById('searchInput').value.trim();
            const side = document.getElementById('sideFilter').value;
            const topic = document.getElementById('topicFilter').value;
            const debateType = document.getElementById('debateTypeFilter').value;

            // Build URL parameters
            const params = new URLSearchParams({
                ...(search && { search }),
                ...(side && { side }),
                ...(topic && { topic }),
                ...(debateType && { debate_type: debateType }),
                page,
                size: 50
            });

            console.log("Query Parameters Sent to Backend:", params.toString());

            try {
                loading = true;
                document.getElementById('loading').style.display = 'block';

                const response = await fetch(`/data?${params}`);
                if (!response.ok) {
                    console.error("Backend Error:", await response.text());
                    alert("Failed to fetch data from backend.");
                    loading = false;
                    document.getElementById('loading').style.display = 'none';
                    return;
                }

                const data = await response.json();
                console.log("Response from Backend:", data);

                // Update the search results count dynamically
                const resultsMessage = document.getElementById("resultsMessage");
                if (data.total === 0 && page === 1) {
                    resultsMessage.textContent = "No results found.";
                } else if (data.total >= 10000) {
                    resultsMessage.textContent = "Showing 10,000+ results.";
                } else {
                    resultsMessage.textContent = `Found ${data.total} result${data.total > 1 ? 's' : ''}`;
                }

                renderCards(data.cards);

                // If fewer cards returned than requested, it means we've hit the end
                if (data.cards.length < 50) {
                    noMoreData = true;
                }

                loading = false;
                document.getElementById('loading').style.display = 'none';

            } catch (err) {
                console.error("Fetch Error:", err);
                alert("Error loading data.");
                loading = false;
                document.getElementById('loading').style.display = 'none';
            }
        }

        // Render cards dynamically
        function renderCards(cards) {
            const container = document.getElementById('cardContainer');
            // If it's the first page and no cards are found, show message
            if (page === 1 && (!cards || cards.length === 0)) {
                container.innerHTML = '<p>No cards found.</p>';
                return;
            }

            // If first page and we have results, clear existing content first
            if (page === 1 && cards.length > 0) {
                container.innerHTML = '';
            }

            // If subsequent pages return no cards, do nothing (no clearing)
            if (!cards || cards.length === 0) {
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
                        <button>${card.debate_type || 'N/A'}</button>
                        <button>${card.topic || 'N/A'}</button>
                    </div>
                    <div class="evidence">${card.evidence?.join('<br>') || 'No evidence'}</div>
                `;
                container.appendChild(cardDiv);
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

        // Apply filters
        function applyFilters() {
            page = 1;
            noMoreData = false;
            fetchData();
        }

        function updateTopics() {
            const debateType = document.getElementById("debateTypeFilter").value;
            const topicLabel = document.querySelector('label[for="topicFilter"]');
            const topicSelect = document.getElementById("topicFilter");

            // If no debate type selected, hide the topics
            if (!debateType) {
                topicLabel.style.display = "none";
                topicSelect.style.display = "none";
                topicSelect.innerHTML = "";
            } else {
                topicLabel.style.display = "inline-block";
                topicSelect.style.display = "inline-block";
                topicSelect.innerHTML = "<option value=''>All Topics</option>";
                if (topics[debateType]) {
                    topics[debateType].forEach(topic => {
                        const option = document.createElement("option");
                        option.value = topic;
                        option.textContent = topic;
                        topicSelect.appendChild(option);
                    });
                }
            }
            page = 1;
            noMoreData = false;
            fetchData();
        }

        function handleScroll() {
            if (noMoreData || loading) return;
            if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 10) {
                page++;
                fetchData();
            }
        }

        // Debounced fetchData for search input
        const debouncedFetchData = debounce(() => {
            page = 1;
            noMoreData = false;
            fetchData();
        }, 300);

        // Initial data load
        fetchData();

        // Add the infinite scroll listener
        window.addEventListener('scroll', handleScroll);
