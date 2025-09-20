// Shutterstock API configuration is now loaded from config.js
// Make sure config.js is included in your HTML file before this script

// Popular search terms for variety
const SEARCH_TERMS = [
    'nature', 'city', 'technology', 'business', 'people', 'food', 'travel',
    'architecture', 'abstract', 'landscape', 'portrait', 'lifestyle', 'sports',
    'animals', 'flowers', 'ocean', 'mountains', 'sunset', 'art', 'design'
];

// Game state
let gameState = {
    currentImage: null,
    originalTitle: '',
    titleWords: [],
    revealedWords: new Set(),
    guessedWords: new Set(),
    score: 0,
    wordsFound: 0,
    totalWords: 0,
    isGameActive: false,
    timeLeft: 60, // 60 seconds
    timerInterval: null,
    isForfeited: false,
    difficulty: 'hard', // 'easy' or 'hard'
    easyModeHiddenWords: [], // Array of 3 random words to hide in easy mode
    persistentDifficulty: 'hard' // Remembers the last selected difficulty mode
};

// DOM elements
const easyModeBtn = document.getElementById('easyModeBtn');
const hardModeBtn = document.getElementById('hardModeBtn');
const btnText = document.querySelector('.btn-text');
const btnLoading = document.querySelector('.btn-loading');
const loadingSpinner = document.getElementById('loadingSpinner');
const imageDisplay = document.getElementById('imageDisplay'); // May be null if element was removed
const errorMessage = document.getElementById('errorMessage'); // May be null if element was removed
const welcomeMessage = document.getElementById('welcomeMessage'); // May be null if element was removed
const guessingInterface = document.getElementById('guessingInterface'); // May be null if element was removed
const gameComplete = document.getElementById('gameComplete'); // May be null if element was removed
const randomImage = document.getElementById('randomImage');
const imageTitle = document.getElementById('imageTitle');
const imageDescription = document.getElementById('imageDescription'); // May be null if element was removed
const imageId = document.getElementById('imageId');
const imageContributor = document.getElementById('imageContributor');
const errorText = document.getElementById('errorText'); // May be null if element was removed

// Header and footer elements
const header = document.querySelector('header');
const footer = document.querySelector('footer');

// Game stats elements
const scoreElement = document.getElementById('score');
const timerElement = document.getElementById('timer');

// Guessing elements
const guessInput = document.getElementById('guessInput');
const guessBtn = document.getElementById('guessBtn');
const forfeitBtn = document.getElementById('forfeitBtn');
const guessFeedback = document.getElementById('guessFeedback');
const guessedWordsList = document.getElementById('guessedWordsList');
const finalScore = document.getElementById('finalScore'); // May be null if element was removed
const playAgainBtn = document.getElementById('playAgainBtn'); // May be null if element was removed

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    easyModeBtn.addEventListener('click', () => {
        gameState.persistentDifficulty = 'easy';
        startNewGame('easy');
    });
    hardModeBtn.addEventListener('click', () => {
        gameState.persistentDifficulty = 'hard';
        startNewGame('hard');
    });
    guessBtn.addEventListener('click', makeGuess);
    forfeitBtn.addEventListener('click', forfeitGame);
    if (playAgainBtn) {
        playAgainBtn.addEventListener('click', startNewGame);
    }
    
    // Enter key support for guessing
    guessInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !guessBtn.disabled && gameState.isGameActive) {
            makeGuess();
        }
    });
    
    // Clear feedback when typing
    guessInput.addEventListener('input', function() {
        clearFeedback();
    });
});

// Start a new game
async function startNewGame(difficulty = 'hard') {
    try {
        resetGameState();
        setLoadingState(true);
        hideAllMessages();
        
        // Get a random search term
        const randomTerm = SEARCH_TERMS[Math.floor(Math.random() * SEARCH_TERMS.length)];
        
        // Make API request - use 'full' view to get higher resolution image URLs
        const response = await fetch(`${SHUTTERSTOCK_CONFIG.baseUrl}/images/search?query=${encodeURIComponent(randomTerm)}&sort=random&per_page=1&view=full`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${SHUTTERSTOCK_CONFIG.accessToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (!data.data || data.data.length === 0) {
            throw new Error('No images found for the search term');
        }
        
        const image = data.data[0];
        setupGame(image, difficulty);
        
    } catch (error) {
        console.error('Error starting new game:', error);
        showError(error.message);
    } finally {
        setLoadingState(false);
    }
}

// Setup the game with a new image
function setupGame(image, difficulty = 'hard') {
    gameState.currentImage = image;
    gameState.originalTitle = image.description || 'Beautiful Stock Photo';
    gameState.titleWords = extractWords(gameState.originalTitle);
    gameState.totalWords = gameState.titleWords.length;
    gameState.isGameActive = true;
    gameState.isForfeited = false;
    gameState.timeLeft = 60;
    gameState.difficulty = difficulty;
    
    // In easy mode, select 3 random words to hide
    if (difficulty === 'easy') {
        const shuffledWords = [...gameState.titleWords].sort(() => Math.random() - 0.5);
        gameState.easyModeHiddenWords = shuffledWords.slice(0, Math.min(3, shuffledWords.length));
    } else {
        gameState.easyModeHiddenWords = [];
    }
    
    // Hide header and footer for cleaner gameplay
    hideHeaderAndFooter();
    
    // Hide the difficulty buttons
    easyModeBtn.style.display = 'none';
    hardModeBtn.style.display = 'none';
    
    // Display the image
    displayImage(image);
    
    // Setup the title display
    displayHiddenTitle();
    
    // Show guessing interface
    if (guessingInterface) {
        guessingInterface.style.display = 'block';
    }
    
    // Update stats
    updateStats();
    
    // Start the timer
    startTimer();
    
    // Focus on input
    guessInput.focus();
}

// Extract words from title (remove punctuation, split by spaces)
function extractWords(title) {
    return title.toLowerCase()
        .replace(/[^\w\s]/g, ' ') // Replace punctuation with spaces
        .split(/\s+/)
        .filter(word => word.length > 0) // Keep all words
        .filter(word => word.length >= 3) // Only words 3+ characters
        .filter(word => !isCommonWord(word)); // Filter out common words
}

// Check if a word is too common to be worth guessing
function isCommonWord(word) {
    const commonWords = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'under', 'over', 'around', 'near', 'far', 'here', 'there', 'where', 'when', 'why', 'how', 'what', 'who', 'which', 'that', 'this', 'these', 'those', 'some', 'any', 'all', 'both', 'each', 'every', 'other', 'another', 'such', 'same', 'different', 'new', 'old', 'good', 'bad', 'big', 'small', 'large', 'little', 'long', 'short', 'high', 'low', 'great', 'first', 'last', 'next', 'previous', 'main', 'major', 'minor', 'important', 'necessary', 'possible', 'available', 'present', 'current', 'recent', 'early', 'late', 'young', 'mature', 'fresh', 'clean', 'dirty', 'hot', 'cold', 'warm', 'cool', 'dry', 'wet', 'full', 'empty', 'open', 'closed', 'free', 'busy', 'ready', 'finished', 'complete', 'partial', 'total', 'whole', 'half', 'quarter', 'double', 'single', 'multiple', 'several', 'many', 'few', 'most', 'least', 'more', 'less', 'much', 'little', 'enough', 'too', 'very', 'quite', 'rather', 'pretty', 'fairly', 'almost', 'nearly', 'about', 'around', 'approximately', 'exactly', 'precisely', 'just', 'only', 'even', 'still', 'yet', 'already', 'soon', 'now', 'then', 'today', 'yesterday', 'tomorrow', 'always', 'never', 'sometimes', 'often', 'usually', 'rarely', 'hardly', 'barely', 'scarcely', 'almost', 'nearly', 'quite', 'rather', 'pretty', 'fairly', 'very', 'extremely', 'highly', 'completely', 'totally', 'entirely', 'fully', 'partly', 'partially', 'mostly', 'mainly', 'primarily', 'especially', 'particularly', 'specifically', 'generally', 'usually', 'normally', 'typically', 'commonly', 'frequently', 'regularly', 'occasionally', 'rarely', 'seldom', 'hardly', 'barely', 'scarcely', 'never', 'always', 'forever', 'permanently', 'temporarily', 'briefly', 'quickly', 'slowly', 'suddenly', 'gradually', 'immediately', 'instantly', 'eventually', 'finally', 'ultimately', 'initially', 'originally', 'previously', 'formerly', 'recently', 'lately', 'currently', 'presently', 'nowadays', 'today', 'tonight', 'tomorrow', 'yesterday', 'this', 'that', 'these', 'those', 'here', 'there', 'where', 'when', 'why', 'how', 'what', 'who', 'which', 'whose', 'whom'];
    return commonWords.includes(word.toLowerCase());
}

// Display the image
function displayImage(image) {
    const imageUrl = getBestImageUrl(image);
    
    if (!imageUrl) {
        throw new Error('No suitable image URL found');
    }
    
    randomImage.src = imageUrl;
    randomImage.alt = image.description || 'Random stock photo';
    
    if (imageDescription) {
        imageDescription.textContent = 'Guess words to reveal the title!';
    }
    imageId.textContent = `ID: ${image.id}`;
    imageContributor.textContent = `Contributor: ${image.contributor || 'Unknown'}`;
    
    if (imageDisplay) {
        imageDisplay.style.display = 'block';
    }
}

// Get the best available image URL from the assets
function getBestImageUrl(image) {
    if (!image.assets) {
        return null;
    }
    
    // Try to get higher resolution images first
    const assetSizes = ['huge', 'large', 'medium', 'small', 'preview'];
    
    for (const size of assetSizes) {
        if (image.assets[size] && image.assets[size].url) {
            // For better quality, try to get the largest available size
            return image.assets[size].url;
        }
    }
    
    return null;
}

// Display the title with hidden words
function displayHiddenTitle() {
    // Get all words from the original title (including small common words)
    const allWords = gameState.originalTitle.toLowerCase()
        .replace(/[^\w\s]/g, ' ')
        .split(/\s+/)
        .filter(word => word.length > 0);
    
    // Create display with all words, but only hide the guessable ones
    const displayWords = allWords.map(word => {
        // If this word is in our guessable words list
        if (gameState.titleWords.includes(word)) {
            // Show it if revealed, hide it if not
            if (gameState.revealedWords.has(word)) {
                return word;
            } else {
                // In easy mode, only hide the pre-selected 3 words
                if (gameState.difficulty === 'easy') {
                    if (gameState.easyModeHiddenWords.includes(word)) {
                        return '_'.repeat(word.length);
                    } else {
                        // Show this word since it's not one of the 3 selected for hiding
                        return word;
                    }
                } else {
                    // Hard mode - hide all guessable words
                    return '_'.repeat(word.length);
                }
            }
        } else {
            // For non-guessable words (small common words), always show them
            return word;
        }
    });
    
    // Now we need to reconstruct the title with original punctuation
    let displayTitle = gameState.originalTitle;
    
    // Replace each word in the original title with our display version
    allWords.forEach((word, index) => {
        const displayWord = displayWords[index];
        // Use word boundaries to ensure we only replace the exact word
        const wordRegex = new RegExp(`\\b${word}\\b`, 'gi');
        displayTitle = displayTitle.replace(wordRegex, displayWord);
    });
    
    imageTitle.textContent = displayTitle;
}

// Make a guess
function makeGuess() {
    if (!gameState.isGameActive || gameState.isForfeited) return;
    
    const guess = guessInput.value.trim().toLowerCase();
    
    if (!guess) {
        showFeedback('Please enter a word to guess!', 'incorrect');
        return;
    }
    
    if (guess.length < 3) {
        showFeedback('Word must be at least 3 characters long!', 'incorrect');
        return;
    }
    
    if (gameState.guessedWords.has(guess)) {
        showFeedback('You already guessed this word!', 'already-guessed');
        guessInput.value = '';
        return;
    }
    
    // Add to guessed words
    gameState.guessedWords.add(guess);
    
    // Check if the word is in the title
    const foundWords = gameState.titleWords.filter(word => word === guess);
    
    if (foundWords.length > 0) {
        // Correct guess!
        foundWords.forEach(word => {
            gameState.revealedWords.add(word);
        });
        
        gameState.score += foundWords.length * 10; // 10 points per word
        
        showFeedback(`Great! Found "${guess}" (${foundWords.length} time${foundWords.length > 1 ? 's' : ''})! +${foundWords.length * 10} points`, 'correct');
        
        // Update display
        displayHiddenTitle();
        updateStats();
        addGuessedWord(guess, true);
        
        // Check if game is complete
        if (gameState.difficulty === 'easy') {
            // In easy mode, complete when all 3 hidden words are revealed
            if (gameState.easyModeHiddenWords.every(word => gameState.revealedWords.has(word))) {
                showFeedback(`Perfect! All words found! +100 completion bonus!`, 'correct');
                completeGame();
            }
        } else {
            // In hard mode, complete when all words are revealed
            if (gameState.revealedWords.size === gameState.titleWords.length) {
                showFeedback(`Perfect! All words found! +100 completion bonus!`, 'correct');
                completeGame();
            }
        }
    } else {
        // Incorrect guess
        showFeedback(`"${guess}" is not in the title. Try again!`, 'incorrect');
        addGuessedWord(guess, false);
    }
    
    guessInput.value = '';
}

// Add a guessed word to the list
function addGuessedWord(word, isCorrect) {
    const wordElement = document.createElement('span');
    wordElement.className = `guessed-word ${isCorrect ? 'correct' : 'incorrect'}`;
    wordElement.textContent = word;
    
    if (!isCorrect) {
        wordElement.style.background = 'linear-gradient(45deg, #e74c3c, #c0392b)';
    }
    
    guessedWordsList.appendChild(wordElement);
}

// Complete the game
function completeGame() {
    gameState.isGameActive = false;
    stopTimer();
    
    // Add 100-point completion bonus
    gameState.score += 100;
    updateStats();
    
    if (guessingInterface) {
        guessingInterface.style.display = 'none';
    }
    
    if (gameComplete) {
        gameComplete.style.display = 'block';
        if (finalScore) {
            finalScore.textContent = gameState.score;
        }
    }
    
    // Show the complete title
    imageTitle.textContent = gameState.originalTitle;
    if (imageDescription) {
        imageDescription.textContent = '🎉 Congratulations! You revealed the complete title! +100 bonus points!';
    }
    
    // Change forfeit button to "New Game"
    changeForfeitToNewGame();
    
    // Show header and footer again
    showHeaderAndFooter();
    
    // Auto-load new image after a short delay using the same difficulty
    setTimeout(() => {
        startNewGame(gameState.persistentDifficulty);
    }, 3000); // 3 seconds to show the complete screen before loading new image
}

// Forfeit the game
function forfeitGame() {
    if (!gameState.isGameActive || gameState.isForfeited) return;
    
    gameState.isForfeited = true;
    gameState.isGameActive = false;
    stopTimer();
    
    // Reveal the complete title
    imageTitle.textContent = gameState.originalTitle;
    if (imageDescription) {
        imageDescription.textContent = '⏰ Time\'s up! The title has been revealed.';
    }
    
    // Disable input and buttons
    if (guessInput) guessInput.disabled = true;
    if (guessBtn) guessBtn.disabled = true;
    if (forfeitBtn) forfeitBtn.disabled = true;
    
    // Show forfeit message
    showFeedback('Game forfeited! The title has been revealed.', 'incorrect');
    
    // Show game complete screen after a short delay
    setTimeout(() => {
        if (guessingInterface) {
            guessingInterface.style.display = 'none';
        }
        
        if (gameComplete) {
            gameComplete.style.display = 'block';
            if (finalScore) {
                finalScore.textContent = gameState.score;
            }
        }
        
        // Keep the default completion message (no time's up message)
        
        // Change forfeit button to "New Game"
        changeForfeitToNewGame();
        
        // Show header and footer again
        showHeaderAndFooter();
        
        // Auto-load new image after showing the complete screen using the same difficulty
        setTimeout(() => {
            startNewGame(gameState.persistentDifficulty);
        }, 3000); // 3 seconds to show the complete screen before loading new image
    }, 2000);
}

// Start the timer
function startTimer() {
    gameState.timerInterval = setInterval(() => {
        gameState.timeLeft--;
        updateTimerDisplay();
        
        if (gameState.timeLeft <= 0) {
            // Time's up - auto forfeit
            forfeitGame();
        }
    }, 1000);
}

// Stop the timer
function stopTimer() {
    if (gameState.timerInterval) {
        clearInterval(gameState.timerInterval);
        gameState.timerInterval = null;
    }
}

// Update timer display
function updateTimerDisplay() {
    const minutes = Math.floor(gameState.timeLeft / 60);
    const seconds = gameState.timeLeft % 60;
    const timeString = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    
    timerElement.textContent = timeString;
    
    // Add visual warnings
    timerElement.className = 'stat-value timer-value';
    if (gameState.timeLeft <= 10) {
        timerElement.classList.add('danger');
    } else if (gameState.timeLeft <= 30) {
        timerElement.classList.add('warning');
    }
}

// Reset game state
function resetGameState() {
    // Stop any running timer
    stopTimer();
    
    gameState = {
        currentImage: null,
        originalTitle: '',
        titleWords: [],
        revealedWords: new Set(),
        guessedWords: new Set(),
        score: gameState.score, // Preserve score across rounds
        wordsFound: 0,
        totalWords: 0,
        isGameActive: false,
        timeLeft: 60,
        timerInterval: null,
        isForfeited: false,
        difficulty: 'hard',
        easyModeHiddenWords: [],
        persistentDifficulty: gameState.persistentDifficulty // Preserve the last selected difficulty
    };
    
    // Clear guessed words list
    guessedWordsList.innerHTML = '';
    
    // Hide game elements
    if (guessingInterface) {
        guessingInterface.style.display = 'none';
    }
    if (gameComplete) {
        gameComplete.style.display = 'none';
    }
    
    // Show the difficulty buttons again
    easyModeBtn.style.display = 'block';
    hardModeBtn.style.display = 'block';
    
    // Reset forfeit button to "Forfeit"
    resetForfeitButton();
    
    // Reset timer display
    timerElement.textContent = '1:00';
    timerElement.className = 'stat-value timer-value';
    
    // Re-enable input and buttons
    if (guessInput) guessInput.disabled = false;
    if (guessBtn) guessBtn.disabled = false;
    if (forfeitBtn) forfeitBtn.disabled = false;
    
    // Show header and footer again
    showHeaderAndFooter();
    
    // Clear feedback
    clearFeedback();
}

// Update game statistics
function updateStats() {
    scoreElement.textContent = gameState.score;
}

// Show feedback message
function showFeedback(message, type) {
    guessFeedback.textContent = message;
    guessFeedback.className = `feedback-text ${type}`;
}

// Clear feedback message
function clearFeedback() {
    guessFeedback.textContent = '';
    guessFeedback.className = 'feedback-text';
}

// Hide header and footer for cleaner gameplay
function hideHeaderAndFooter() {
    if (header) header.classList.add('hidden');
    if (footer) footer.classList.add('hidden');
}

// Show header and footer
function showHeaderAndFooter() {
    if (header) header.classList.remove('hidden');
    if (footer) footer.classList.remove('hidden');
}

// Change forfeit button to "New Game"
function changeForfeitToNewGame() {
    forfeitBtn.textContent = 'New Game';
    forfeitBtn.style.background = 'linear-gradient(45deg, #27ae60, #2ecc71)';
    forfeitBtn.style.boxShadow = '0 4px 15px rgba(39, 174, 96, 0.4)';
    
    // Remove old event listener and add new one
    forfeitBtn.removeEventListener('click', forfeitGame);
    forfeitBtn.addEventListener('click', startNewGame);
}

// Reset forfeit button to "Forfeit"
function resetForfeitButton() {
    forfeitBtn.textContent = 'Forfeit';
    forfeitBtn.style.background = 'linear-gradient(45deg, #e74c3c, #c0392b)';
    forfeitBtn.style.boxShadow = '0 4px 15px rgba(231, 76, 60, 0.4)';
    
    // Remove old event listener and add new one
    forfeitBtn.removeEventListener('click', startNewGame);
    forfeitBtn.addEventListener('click', forfeitGame);
}

// Set loading state
function setLoadingState(isLoading) {
    if (isLoading) {
        easyModeBtn.disabled = true;
        hardModeBtn.disabled = true;
        // Hide button text and show loading for both buttons
        easyModeBtn.querySelector('.btn-text').style.display = 'none';
        hardModeBtn.querySelector('.btn-text').style.display = 'none';
        easyModeBtn.querySelector('.btn-loading').style.display = 'inline';
        hardModeBtn.querySelector('.btn-loading').style.display = 'inline';
        loadingSpinner.style.display = 'block';
    } else {
        easyModeBtn.disabled = false;
        hardModeBtn.disabled = false;
        // Show button text and hide loading for both buttons
        easyModeBtn.querySelector('.btn-text').style.display = 'inline';
        hardModeBtn.querySelector('.btn-text').style.display = 'inline';
        easyModeBtn.querySelector('.btn-loading').style.display = 'none';
        hardModeBtn.querySelector('.btn-loading').style.display = 'none';
        loadingSpinner.style.display = 'none';
    }
}

// Show error message
function showError(message) {
    if (errorText) errorText.textContent = message;
    if (errorMessage) errorMessage.style.display = 'block';
}

// Hide all messages
function hideAllMessages() {
    if (imageDisplay) imageDisplay.style.display = 'none';
    if (errorMessage) errorMessage.style.display = 'none';
    if (welcomeMessage) welcomeMessage.style.display = 'none';
    if (guessingInterface) guessingInterface.style.display = 'none';
    if (gameComplete) gameComplete.style.display = 'none';
}

// Handle image load errors
randomImage.addEventListener('error', function() {
    showError('Failed to load the image. Please try again.');
    setLoadingState(false);
});

// Add some fun interactions
newImageBtn.addEventListener('mouseenter', function() {
    if (!this.disabled) {
        this.style.transform = 'translateY(-2px) scale(1.05)';
    }
});

newImageBtn.addEventListener('mouseleave', function() {
    if (!this.disabled) {
        this.style.transform = 'translateY(0) scale(1)';
    }
});

// Add keyboard support for new game
document.addEventListener('keydown', function(event) {
    if (event.code === 'Space' && !easyModeBtn.disabled && !gameState.isGameActive) {
        event.preventDefault();
        startNewGame(gameState.persistentDifficulty); // Use the last selected difficulty
    }
});

// Add visual feedback for successful image loads
randomImage.addEventListener('load', function() {
    this.style.opacity = '0';
    this.style.transform = 'scale(0.9)';
    
    setTimeout(() => {
        this.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        this.style.opacity = '1';
        this.style.transform = 'scale(1)';
    }, 50);
});