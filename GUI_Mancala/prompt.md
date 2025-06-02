Mancala Game Development Prompt

Create a complete Mancala (Kalah variant) game in Python with the following specifications:
Core Game Requirements

    Rules: Traditional 6-pit Kalah Mancala with 4 seeds per pit initially
    Players: Two players (Player 1 and Player 2) taking turns
    Winning condition: Player with most seeds in their store wins
    Game mechanics:
        Sow seeds counter-clockwise
        Extra turn when last seed lands in own store
        Capture opponent's seeds when last seed lands in empty own pit
        Game ends when one side is completely empty

GUI Requirements

    Framework: Use tkinter for the GUI (built-in Python library)
    Layout:
        Horizontal board layout with pits clearly labeled
        Two stores (Mancalas) on opposite ends
        Current player indicator
        Score display
        Game status messages

Visual Design

    Graphics:
        Use colored circles/ovals for pits and stores
        Animate seed movement during turns
        Visual seed counters (small circles or numbers)
        Different colors for each player's side
    Icons:
        Seeds represented as small colored dots
        Player indicators (arrows or highlighting)
        Reset/New Game button with icon
    Polish:
        Smooth animations for seed distribution
        Hover effects on clickable pits
        Clean, modern color scheme
        Responsive button states

Technical Features

    Game Logic: Complete rule implementation with validation
    AI Option: Simple AI opponent (optional but preferred)
    Game Controls:
        Click pits to make moves
        New game/reset functionality
        Move history display
    Error Handling: Prevent invalid moves with user feedback

Code Structure

    Object-oriented design with separate classes for:
        Game logic (MancalaGame)
        GUI interface (MancalaGUI)
        Game board state (Board)
    Clean, documented code with proper separation of concerns

Deliverable: A single Python file that runs a complete, playable Mancala game with professional-looking graphics and smooth user experience.