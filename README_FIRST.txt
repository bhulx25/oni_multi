ONI RENDER — THREE-ENVIRONMENT TABLE VERSION

WHAT IS NEW
- The complete Head-to-Head screen is compact so the table, seats, Benny,
  turn message, timer and player controls fit together on laptop and iPad screens.
- Head-to-Head action controls now sit directly below the table. The active
  player sees Check/Bet/Fold or Call/Raise/Fold; the other player sees the
  same control area disabled until the turn changes.
- New compact square casino table for Play Benny and multiplayer modes.
- Colorful player avatars replace the earlier plain seat boxes.
- Benny uses the raised-visor portrait so his eyes are visible.
- A face-down undealt deck is displayed in front of Benny.
- The casino has exactly three play choices: Play Benny, Head-to-Head,
  and Multi Table. Private tables and join codes were removed.
- The active seat displays blinking cartoon ??? marks without repeatedly
  refreshing and flashing the entire page.
- A visible 45-second turn timer automatically folds a timed-out player
  when facing a bet, or automatically checks when no bet is owed.
- Players can pause or resume their seat; a paused seat sits out future hands.
- The live pot balance is displayed on the table.
- Separate Play Benny game remains available.
- Head-to-Head tables accept exactly two human players.
- Multi Tables can start with two and accept up to six human players.
- Benny is the dealer only and never occupies a player seat.
- Open tables are listed in the appropriate lobby and can be joined directly.
- Players may join a waiting list and seated players may invite them.
- A player may leave at any time. An empty table is cleared and returned
  to service so it can be reused.
- Each player sees every opponent's card, but the server never sends that
  player their own card value while the hand is active.
- Opponent cards sit in a card holder until LOOK AT THE OTHER CARDS is
  pressed. The open holder appears in front of the player and stays open
  across turn updates until the player closes it.
- The first player rotates every hand.
- If everyone checks once, only the first player gets the final option to
  Double Check or Bet.
- Multiplayer betting includes Check, Bet, Call, Raise, Fold and all-in calls.
- Side pots are settled when players have different all-in amounts.
- Benny never calls when the visible human card is an Ace; his only
  aggressive Ace response is an occasional bluff raise.
- A broke player is offered a clearly labeled 1,000-Test-Cryptino refill;
  this demonstration button does not process a real payment.

LOCAL TEST
1. Install requirements: python -m pip install -r requirements.txt
2. Run: python oni_multi_6_player.py
3. Open http://127.0.0.1:5005
4. For multiple players, use separate browsers/devices and different names.

RENDER
- Build command: pip install -r requirements.txt
- Start command: gunicorn oni_multi_6_player:app --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 120

IMPORTANT TEST-SERVER LIMITATION
Player accounts, waiting lists, tables and hands are currently stored in memory. A server
restart resets them. Keep one Gunicorn worker for this test version. Before a
large public launch, move this state to a shared database such as PostgreSQL.
