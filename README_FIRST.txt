ONI INVESTOR TEASER V2_MULTI — TEST VERSION

Purpose:
- Test multiple named players against Benny at the same time.
- Each player name has its own account/balance record.
- Each Benny game gets its own unique match ID and game state.
- One player's cards, pot, bets, or Benny balance should not alter another player's game.

IMPORTANT TEST METHOD:
1. Start the server normally on port 5005.
2. Use separate browsers/devices for separate players (example: PC = Bill, iPad = John).
   A single browser shares one login session, so logging in as a different name there changes that browser's current player.
3. Have both players enter different names and choose Play ONI vs Benny.
4. Compare cards, pot, balances and actions. They should remain independent.

This is still an in-memory test server. If the Python process is restarted, player/game memory resets.
For a finished public site, persistent accounts and multi-worker-safe storage/database will be added.
