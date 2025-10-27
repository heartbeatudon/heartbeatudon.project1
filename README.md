# Heartbeat Udon Adventure

A bite-sized text adventure that you can play right in the terminal. Explore a
mysterious forest, gather a few essential items, and claim the relic hidden in
an abandoned watchtower.

## Getting Started

1. Ensure you have Python 3.9 or later installed.
2. (Optional) Create and activate a virtual environment.
3. Install the development dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

   If you don't plan to run the tests, you can skip this step.

4. Launch the game:

   ```bash
   python main.py
   ```

   Follow the prompts and type commands such as `north`, `take torch`, or
   `inventory` to interact with the world.

## Running Tests

Automated tests verify a few core pieces of game logic. To run them, install
`pytest` (included in `requirements-dev.txt`) and execute:

```bash
python -m pytest
```
