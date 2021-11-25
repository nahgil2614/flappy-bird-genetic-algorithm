# flappy-bird-genetic-algorithm
🐦 Self-taught birds trying to survive the harsh world of Flappy Bird.

## The learning process
Each bird is equipped with a brain that evolves generation-by-generation by the following mechanism:
- Each generation has 100 birds, the worst 50 (which die the earliest) will be eliminated.
- Each of the 50 surviving birds reproduces asexually, its genes are passed down to its two hatchlings: the first one will inherit the full genes, the second one will inherit the mutated genes.
- The process repeats.

## How to run
```
python3 game_nn_resizable.py
```

## Shortcuts
Here are some keyboard shortcuts for better experience:
- Space: pause the learning process
- Right arrow: speed up the learning process by 2 times
- Left arrow: slow down the learning process by 2 times
- Escape: close the game

## Annotations
Each generation will have 4 special birds being circled:
- 🟥 Red circle: the hatchling of the best bird of the last generation (full genes)
- 🟨 Yellow circle: the hatchling of the best bird of the last generation (mutated genes)
- ⬛ Black circle: the hatchling of the worst bird of the last generation (full genes)
- ⬜ White circle: the hatchling of the worst bird of the last generation (mutated genes)

## Lessons learnt
- Use pygame to build games.
- Get familiar with genetic algorithm.

## Credits
I was able to build the core game logic (the `game.py` file) for this project thanks to [this](https://www.youtube.com/watch?v=UZg49z76cLw) clear and concise tutorial on pygame from [Clear Code](https://www.youtube.com/channel/UCznj32AM2r98hZfTxrRo9bQ).