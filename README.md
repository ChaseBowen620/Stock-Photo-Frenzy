# Stock Photo Word Guessing Game 🎯

A fun and engaging word guessing game that uses random images from the Shutterstock API. Players guess words that appear in the image titles to reveal them and earn points!

## Features

- 🎯 **Word Guessing Game**: Guess words in image titles to reveal them
- 🏆 **Scoring System**: Earn 10 points for each correct word
- ⏰ **One-Minute Timer**: Race against the clock to guess all words
- 🚩 **Forfeit Button**: Give up and reveal the title if you're stuck
- 🎲 **Random Images**: Get random images from Shutterstock's vast collection
- 🎨 **Modern UI**: Clean, responsive design with smooth animations
- 📱 **Mobile Friendly**: Works perfectly on all devices
- ⌨️ **Keyboard Support**: Press Enter to submit guesses, Spacebar for new game
- 🛡️ **Error Handling**: Graceful error handling with user-friendly messages
- 🎉 **Game Completion**: Celebrate when you reveal the complete title!

## How to Play

1. **Start New Game**: Click "Start New Game" to get a random image
2. **Race Against Time**: You have 60 seconds to guess all words in the title
3. **Guess Words**: Type words you think might be in the image title
4. **Earn Points**: Get 10 points for each correct word you guess
5. **Reveal Title**: Watch as correct words appear in the title
6. **Complete the Game**: Reveal all words to win before time runs out!
7. **Forfeit if Stuck**: Click "Forfeit" to reveal the title and end the game
8. **Play Again**: Start a new game with a different image

## Game Rules

- **Time Limit**: You have exactly 60 seconds per game
- **Word Requirements**: Words must be at least 3 characters long
- **Smart Filtering**: Common words (the, and, etc.) are filtered out
- **No Duplicates**: You can't guess the same word twice
- **Scoring**: Each correct word gives you 10 points
- **Game End**: The game ends when you reveal all words OR time runs out OR you forfeit
- **Auto-Forfeit**: If the timer reaches 0:00, the game automatically forfeits

## Technical Details

- **Frontend**: Pure HTML, CSS, and JavaScript (no frameworks required)
- **API**: Shutterstock API v2
- **Authentication**: Uses your provided access token
- **Search Strategy**: Randomly selects from popular search terms for variety

## Files Structure

```
├── index.html          # Main HTML structure
├── styles.css          # CSS styling and responsive design
├── script.js           # JavaScript for API calls and interactions
└── README.md           # This file
```

## API Configuration

The app is pre-configured with your Shutterstock API credentials:
- **Consumer Key**: Q7APIXat48bXGNxoCK8aJwhTvPd50Bmd
- **Access Token**: Your provided token is embedded in the JavaScript

## Browser Compatibility

- ✅ Chrome (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile browsers

## Troubleshooting

If you encounter issues:

1. **Check Internet Connection**: Ensure you have a stable internet connection
2. **API Limits**: Your Shutterstock API may have rate limits
3. **Browser Console**: Check the browser's developer console for error messages
4. **CORS Issues**: If running locally, some browsers may block API calls - try using a local server

## Game Features

- **Smart Word Filtering**: Automatically filters out common words to make the game more challenging
- **Visual Feedback**: Color-coded feedback for correct/incorrect guesses
- **Progress Tracking**: Real-time score and word count updates
- **Guessed Words List**: Keep track of all your attempts
- **Timer Display**: Visual countdown with color-coded warnings (yellow at 30s, red at 10s)
- **Forfeit Option**: Give up anytime to see the complete title
- **Auto-Forfeit**: Game automatically ends when time runs out
- **Responsive Design**: Play on desktop, tablet, or mobile
- **Smooth Animations**: Enjoyable visual effects when words are revealed

## Future Enhancements

Potential improvements you could add:
- Difficulty levels (easy/medium/hard)
- Time-based challenges
- Multiplayer mode
- Word hints system
- Achievement badges
- High score leaderboard
- Custom word categories
- Sound effects and music

## License

This project uses the Shutterstock API. Please ensure you comply with Shutterstock's terms of service and licensing requirements for any images you use.

---

**Have fun guessing words and discovering amazing images!** 🎯🎉
