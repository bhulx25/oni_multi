from flask import Flask, redirect, render_template_string, request, session, url_for
import random
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

STARTING_BALANCE = 1000
ANTE = 10
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANK_VALUE = {rank: value for value, rank in enumerate(RANKS, 2)}
SUIT_SYMBOL = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}

players = {}
matches = {}
waiting_player = None

PAGE = '''<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ONI V2 MULTI — Cryptino Casino</title>
<style>
:root{
  --bg:#080b16; --panel:#111827; --panel2:#171f32; --gold:#f3c75f;
  --gold2:#ffe49a; --text:#f8fafc; --muted:#aeb9cc; --green:#0e6b45;
  --red:#9f2636; --line:#2a354d;
}
*{box-sizing:border-box}
body{
  margin:0;color:var(--text);font-family:Arial,Helvetica,sans-serif;
  background:
    radial-gradient(circle at 20% 0%,#17345b 0,#0c172b 28%,transparent 52%),
    radial-gradient(circle at 85% 12%,#3a1c54 0,transparent 35%),
    var(--bg);
  min-height:100vh;
}
.site{max-width:1180px;margin:auto;padding:18px}
.topbar{
  display:flex;align-items:center;justify-content:space-between;gap:18px;
  padding:12px 4px 22px;border-bottom:1px solid #ffffff18;
}
.brand{display:flex;align-items:center;gap:12px}
.logo-mark{
  width:50px;height:50px;border-radius:14px;display:grid;place-items:center;
  font-weight:900;font-size:25px;color:#111;background:linear-gradient(145deg,var(--gold2),#b9862d);
  box-shadow:0 0 28px #f3c75f33;
}
.brand-title{font-weight:900;letter-spacing:2px;font-size:20px}
.brand-sub{color:var(--muted);font-size:12px;letter-spacing:1.5px}
.nav{color:var(--muted);font-size:14px}
.nav span{margin-left:18px}
.shell{padding:34px 0}
.hero{
  display:grid;grid-template-columns:1.2fr .8fr;gap:28px;align-items:center;
  padding:34px;border:1px solid #ffffff16;border-radius:26px;
  background:linear-gradient(145deg,#121b2d,#0d1220);
  box-shadow:0 22px 70px #0008;
}
.eyebrow{color:var(--gold);font-weight:800;letter-spacing:2px;text-transform:uppercase;font-size:13px}
h1{font-size:clamp(44px,7vw,76px);line-height:.95;margin:10px 0 14px;letter-spacing:-2px}
h2{color:var(--gold2);margin-top:6px}
.lead{font-size:19px;line-height:1.6;color:#d5dcea;max-width:720px}
.badges{display:flex;gap:9px;flex-wrap:wrap;margin:20px 0}
.badge{padding:8px 11px;border-radius:999px;background:#ffffff0c;border:1px solid #ffffff18;color:#dce4f2;font-size:13px}
.actions{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:15px}
.hero .actions{justify-content:flex-start}
button,.button,input{
  font-size:17px;padding:12px 18px;border-radius:10px;border:1px solid transparent
}
button,.button{
  background:linear-gradient(145deg,var(--gold2),var(--gold));color:#16130c;
  cursor:pointer;font-weight:800;text-decoration:none;box-shadow:0 8px 25px #0005
}
button:hover,.button:hover{filter:brightness(1.07)}
.secondary{background:#26324a;color:white;border-color:#3c4a68}
.danger{background:#352330;color:#ffd5dc;border-color:#67313d}
.login-card,.game-card,.vision-card{
  background:#101827;border:1px solid #ffffff16;border-radius:20px;padding:24px;
}
.login-card{box-shadow:inset 0 1px #ffffff12}
.kicker{color:var(--muted);font-size:14px}
input{width:min(300px,100%);background:#090e19;color:white;border-color:#35415a}
.balance-pill{
  display:inline-block;margin:8px 0 18px;padding:10px 15px;border-radius:999px;
  background:#0f2e26;border:1px solid #2f795e;color:#bff5df;font-weight:700
}
.game-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:22px}
.game-card{min-height:165px;text-align:left}
.game-card h3{margin:8px 0;font-size:23px}
.game-card p{color:var(--muted);line-height:1.5}
.game-card.coming{opacity:.62}
.oni-icon{font-size:36px}
.vision{
  margin-top:24px;display:grid;grid-template-columns:repeat(4,1fr);gap:12px
}
.vision-card strong{display:block;color:var(--gold2);margin-bottom:7px}
.vision-card span{color:var(--muted);font-size:14px;line-height:1.45}
.footer-note{margin:28px 0 5px;color:#7f8ba1;font-size:12px;text-align:center}
.box{
  max-width:900px;margin:0 auto;padding:26px;background:#101827;border:1px solid #ffffff17;
  border-radius:22px;box-shadow:0 18px 55px #0008;text-align:center
}
.balances{
  display:flex;justify-content:space-around;gap:12px;font-size:20px;background:#0a101d;
  padding:13px;border:1px solid #25314a;border-radius:12px;flex-wrap:wrap
}
.card{
  display:inline-flex;width:150px;height:210px;background:white;color:#111;border-radius:14px;
  align-items:center;justify-content:center;font-size:27px;font-weight:bold;
  box-shadow:3px 5px 18px #0009;margin:18px
}
.red{color:#c7192d}
.pot{font-size:26px;color:var(--gold)}
.message{min-height:28px;font-size:19px;margin:14px}
.note{font-size:14px;color:var(--muted)}
.waiting{font-size:22px;padding:18px;background:#0a101d;border-radius:12px;margin:18px 0}
.benny-row{
  display:flex;align-items:center;justify-content:center;gap:16px;margin:12px auto 4px;
  padding:12px 16px;background:#0a101d;border:1px solid #293752;border-radius:16px;max-width:520px
}
.benny-avatar{
  width:86px;height:86px;border-radius:50%;object-fit:cover;border:3px solid var(--gold);
  box-shadow:0 0 26px #f3c75f33
}
.benny-name{text-align:left}
.benny-name strong{font-size:25px;color:var(--gold2)}
.benny-name span{display:block;color:var(--muted);margin-top:3px}
a{color:var(--gold2)}
@media(max-width:800px){
  .hero{grid-template-columns:1fr;padding:24px}
  .game-grid{grid-template-columns:1fr}
  .vision{grid-template-columns:1fr 1fr}
  .nav{display:none}
}
@media(max-width:520px){.vision{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="site">
  <div class="topbar">
    <div class="brand">
      <div class="logo-mark">C</div>
      <div><div class="brand-title">CRYPTINO CASINO</div><div class="brand-sub">PLAY • COMPETE • EXPAND</div></div>
    </div>
    <div class="nav"><span>Lobby</span><span>Games</span><span>Wallet</span><span>Vision</span></div>
  </div>
  <div class="shell">{{ body|safe }}</div>
  <div class="footer-note">Investor demonstration • Cryptinos shown here are prototype game credits only.</div>
</div>
</body></html>'''

HOME = '''<section class="hero">
<div>
  <div class="eyebrow">V2 MULTI TEST • Separate Benny game for each player name</div>
  <h1>ONI</h1>
  <p class="lead">One card. Hidden information. Fast decisions. ONI is the teaser for a multi-game competitive casino platform built around Cryptinos.</p>
  <div class="badges">
    <span class="badge">Fast-play poker</span>
    <span class="badge">Computer opponent</span>
    <span class="badge">Two-player mode</span>
    <span class="badge">Expandable game lobby</span>
  </div>
  {% if name %}
    <div class="balance-pill">{{ name }} • {{ balance }} Cryptinos</div>
    <div class="actions">
      <form method="post" action="{{ url_for('play_benny') }}"><button>Play ONI vs Benny</button></form>
      <form method="post" action="{{ url_for('join_two_player') }}"><button class="secondary">Challenge a Player</button></form>
    </div>
    <p class="note"><a href="{{ url_for('logout') }}">Change player</a></p>
  {% else %}
    <form method="post" action="{{ url_for('login') }}">
      <p><input name="name" placeholder="Enter player name" maxlength="30" required></p>
      <button>Enter the Casino</button>
    </form>
  {% endif %}
</div>
<div class="login-card">
  <div class="eyebrow">Featured opponent</div>
  <img src="/static/benny.png" alt="Benny computer opponent" style="width:180px;height:180px;border-radius:50%;object-fit:cover;border:4px solid #f3c75f;box-shadow:0 0 40px #f3c75f33">
  <h2 style="margin-bottom:5px">Meet Benny</h2>
  <p class="kicker">ONI's computer avatar. He checks, bets, raises, folds—and occasionally bluffs.</p>
  <div class="balance-pill">Computer Opponent • Ready</div>
</div>
</section>

<div class="game-grid">
  <div class="game-card">
    <div class="oni-icon">♠</div><h3>ONI</h3>
    <p>The launch game: one-card poker where you see your opponent's card, but not your own.</p>
  </div>
  <div class="game-card coming">
    <div class="oni-icon">♦</div><h3>Game Two</h3>
    <p>A second Cryptino-powered game can plug into the same player, lobby, and balance ecosystem.</p>
  </div>
  <div class="game-card coming">
    <div class="oni-icon">♣</div><h3>Casino Expansion</h3>
    <p>Additional games, tournaments, rankings, player identities, and competitive formats.</p>
  </div>
</div>

<div class="vision">
  <div class="vision-card"><strong>ONE ECOSYSTEM</strong><span>Multiple games connected through one recognizable casino experience.</span></div>
  <div class="vision-card"><strong>CRYPTINOS</strong><span>A common in-game accounting unit for the prototype platform.</span></div>
  <div class="vision-card"><strong>PLAYER NETWORK</strong><span>Computer play today; matchmaking, profiles, ratings, and tournaments next.</span></div>
  <div class="vision-card"><strong>BUILT TO EXPAND</strong><span>ONI demonstrates the platform while the game catalog grows around it.</span></div>
</div>'''

BENNY_GAME = '''<div class="box">
<div class="eyebrow">CRYPTINO CASINO • FEATURED GAME</div>
<h1 style="font-size:54px">ONI</h1>
<div class="benny-row">
  <img class="benny-avatar" src="/static/benny.png" alt="Benny">
  <div class="benny-name"><strong>Benny</strong><span>Computer Opponent • ONI House Player</span></div>
</div>
<div class="balances"><span>{{ name }}: <b>{{ player_balance }}</b> Cryptinos</span><span>Benny: <b>{{ benny_balance }}</b> Cryptinos</span></div>
<p class="pot">Pot: {{ match.pot }} Cryptinos</p>
<p>You can see Benny's card—but not your own.</p>
<div class="card {% if match.cards.Benny.suit in ['Hearts','Diamonds'] %}red{% endif %}">{{ match.cards.Benny.rank }}<br>{{ symbols[match.cards.Benny.suit] }}</div>
<div class="message">{{ match.message }}</div>
{% if match.benny_folded %}<script>window.addEventListener('load', function(){ window.alert('Benny folds'); });</script>{% endif %}
{% if match.status == 'active' %}
<form id="actionForm" method="post" action="{{ url_for('benny_action', match_id=match.id) }}">
<input type="hidden" id="actionField" name="action" value=""><input type="hidden" id="amountField" name="amount" value="">
<div class="actions">{% if match.to_call > 0 %}<button type="button" onclick="submitSimple('call')">Call {{ match.to_call }}</button><button type="button" onclick="openAmountBox('raise')">Raise</button>{% else %}<button type="button" onclick="submitSimple('check')">Check</button><button type="button" onclick="openAmountBox('bet')">Bet</button>{% endif %}<button type="button" class="danger" onclick="submitSimple('fold')">Fold</button></div>
<p class="note">Bet and Raise open a clearly visible amount box.</p></form>
<div id="amountOverlay" style="display:none;position:fixed;inset:0;background:#000b;z-index:9999;align-items:center;justify-content:center;padding:20px">
  <div style="width:min(430px,95vw);background:#101827;border:2px solid #f3c75f;border-radius:18px;padding:24px;text-align:center;box-shadow:0 20px 70px #000">
    <h2 id="amountTitle" style="margin-top:0">Enter amount</h2>
    <p id="amountHelp" class="note" style="font-size:16px"></p>
    <input id="amountEntry" type="number" min="1" step="1" inputmode="numeric" style="width:180px;text-align:center;font-size:22px" autofocus>
    <div class="actions"><button type="button" onclick="confirmAmount()">Enter</button><button type="button" class="secondary" onclick="closeAmountBox()">Cancel</button></div>
    <div id="amountError" style="color:#ffd5dc;min-height:24px;margin-top:8px"></div>
  </div>
</div>
<script>
let pendingAmountAction='';
function submitSimple(action){document.getElementById('actionField').value=action;document.getElementById('amountField').value='';document.getElementById('actionForm').submit();}
function openAmountBox(action){
  pendingAmountAction=action;
  const balance={{ player_balance|int }};
  const toCall={{ match.to_call|int }};
  const maxAmount=action==='raise'?Math.max(0,balance-toCall):balance;
  document.getElementById('amountTitle').textContent=action==='raise'?'How much do you want to RAISE?':'How much do you want to BET?';
  document.getElementById('amountHelp').textContent='Available amount: '+maxAmount;
  const entry=document.getElementById('amountEntry'); entry.value=''; entry.max=String(maxAmount);
  document.getElementById('amountError').textContent='';
  document.getElementById('amountOverlay').style.display='flex';
  setTimeout(()=>entry.focus(),50);
}
function closeAmountBox(){document.getElementById('amountOverlay').style.display='none';pendingAmountAction='';}
function confirmAmount(){
  const entry=document.getElementById('amountEntry');
  const amount=Number(entry.value); const maxAmount=Number(entry.max);
  if(!Number.isInteger(amount)||amount<=0){document.getElementById('amountError').textContent='Enter a whole number greater than 0.';return;}
  if(amount>maxAmount){document.getElementById('amountError').textContent='Maximum available: '+maxAmount;return;}
  document.getElementById('actionField').value=pendingAmountAction;
  document.getElementById('amountField').value=String(amount);
  document.getElementById('amountOverlay').style.display='none';
  document.getElementById('actionForm').submit();
}
document.addEventListener('keydown',function(e){if(document.getElementById('amountOverlay').style.display==='flex'){if(e.key==='Escape')closeAmountBox();if(e.key==='Enter'){e.preventDefault();confirmAmount();}}});
</script>
{% else %}
<h3>Your hidden card was:</h3>
<div class="card {% if match.cards[name].suit in ['Hearts','Diamonds'] %}red{% endif %}">{{ match.cards[name].rank }}<br>{{ symbols[match.cards[name].suit] }}</div>
<div class="actions"><form method="post" action="{{ url_for('play_benny') }}"><button>Play Benny Again</button></form><a class="button secondary" href="{{ url_for('index') }}">Casino Lobby</a></div>
{% endif %}
</div>'''

WAITING = '''<h1>ONIONI</h1><h2>Two-player game</h2><div class="waiting">{{ message }}</div>
{% if match_id %}<p><a href="{{ url_for('two_game', match_id=match_id) }}">Enter Match</a></p>{% else %}<p class="note">Leave this page open. It refreshes automatically.</p><script>setTimeout(function(){location.reload();},2000);</script>{% endif %}
<p><a href="{{ url_for('cancel_waiting') }}">Cancel and return to main menu</a></p>'''

TWO_GAME = '''<h1>ONIONI</h1><p class="note" style="font-size:22px;color:#fff;background:#8b0000;padding:8px;border-radius:8px"><b>ONI INVESTER TEASER V2 — TWO PLAYER</b></p>
<div class="balances"><span>{{ name }}: <b>{{ my_balance }}</b></span><span>{{ opponent }}: <b>{{ opp_balance }}</b></span></div>
<p class="pot">Pot: {{ match.pot }} Cryptinos</p>
<p>You can see {{ opponent }}'s card—but not your own.</p>
<div class="card {% if match.cards[opponent].suit in ['Hearts','Diamonds'] %}red{% endif %}">{{ match.cards[opponent].rank }}<br>{{ symbols[match.cards[opponent].suit] }}</div>
<div class="message">{{ match.message }}</div>
{% if match.status == 'active' %}
{% if match.turn == name %}
<form id="twoActionForm" method="post" action="{{ url_for('two_action', match_id=match.id) }}"><input type="hidden" id="twoActionField" name="action" value=""><input type="hidden" id="twoAmountField" name="amount" value=""><div class="actions">
{% if match.to_call > 0 %}<button type="button" onclick="twoSimple('call')">Call {{ match.to_call }}</button><button type="button" onclick="twoAsk('raise')">Raise</button>{% else %}<button type="button" onclick="twoSimple('check')">Check</button><button type="button" onclick="twoAsk('bet')">Bet</button>{% endif %}<button type="button" class="danger" onclick="twoSimple('fold')">Fold</button></div></form>
<script>
function twoSimple(action){document.getElementById('twoActionField').value=action;document.getElementById('twoAmountField').value='';document.getElementById('twoActionForm').submit();}
function twoAsk(action){const balance={{ my_balance|int }};const toCall={{ match.to_call|int }};const maxAmount=action==='raise'?balance-toCall:balance;const label=action==='raise'?'How much do you want to RAISE?':'How much do you want to BET?';const answer=window.prompt(label+'\\nAvailable amount: '+maxAmount);if(answer===null)return;const amount=Number(answer);if(!Number.isInteger(amount)||amount<=0){window.alert('Please enter a whole number greater than 0.');return;}if(amount>maxAmount){window.alert('That is more than your available bank. Maximum: '+maxAmount);return;}document.getElementById('twoActionField').value=action;document.getElementById('twoAmountField').value=String(amount);document.getElementById('twoActionForm').submit();}
</script>
{% else %}<p class="waiting">Waiting for {{ opponent }} to act…</p><script>setTimeout(function(){location.reload();},1500);</script>{% endif %}
{% else %}<h3>Your hidden card was:</h3><div class="card {% if match.cards[name].suit in ['Hearts','Diamonds'] %}red{% endif %}">{{ match.cards[name].rank }}<br>{{ symbols[match.cards[name].suit] }}</div><h3>{{ match.result }}</h3><div class="actions"><form method="post" action="{{ url_for('rematch', match_id=match.id) }}"><button>Play Again</button></form><form method="post" action="{{ url_for('join_two_player') }}"><button class="secondary">New Opponent</button></form></div><p><a href="{{ url_for('index') }}">Main menu</a></p>{% endif %}'''

def new_card(exclude=None):
    while True:
        card = {'rank': random.choice(RANKS), 'suit': random.choice(SUITS)}
        if card != exclude:
            return card

def player_record(name):
    account = players.setdefault(name, {'balance': STARTING_BALANCE, 'benny_balance': STARTING_BALANCE, 'match_id': None, 'benny_match_id': None})
    account.setdefault('benny_balance', STARTING_BALANCE)
    account.setdefault('match_id', None)
    account.setdefault('benny_match_id', None)
    return account

def page(body, **values):
    inner = render_template_string(body, **values)
    return render_template_string(PAGE, body=inner)

# ---------------- Benny mode: preserved from poker_4 ----------------
def finish_benny(match, winner, message):
    match['status'] = 'finished'; match['winner'] = winner; match['message'] = message
    if winner == 'tie':
        half = match['pot'] // 2; match['player_balance'] += half; match['benny_balance'] += match['pot'] - half
    elif winner == match['player']: match['player_balance'] += match['pot']
    else: match['benny_balance'] += match['pot']
    players[match['player']]['balance'] = match['player_balance']; players[match['player']]['benny_balance'] = match['benny_balance']

def showdown_benny(match, prefix=''):
    human = match['player']; mine = RANK_VALUE[match['cards'][human]['rank']]; his = RANK_VALUE[match['cards']['Benny']['rank']]
    if mine > his: finish_benny(match, human, prefix + ' You win the showdown!')
    elif his > mine: finish_benny(match, 'Benny', prefix + ' Benny wins the showdown.')
    else: finish_benny(match, 'tie', prefix + ' Tie hand. The pot is split.')

def take_benny_bet(match, who, amount):
    key = 'player_balance' if who == match['player'] else 'benny_balance'; amount = min(amount, match[key]); match[key] -= amount; match['pot'] += amount; return amount

def benny_after_player_check(match):
    seen = RANK_VALUE[match['cards'][match['player']]['rank']]; roll = random.random()
    if seen >= 11: choice = 'bet' if roll < 0.20 else 'check'
    elif seen >= 7: choice = 'bet' if roll < 0.45 else 'check'
    else: choice = 'bet' if roll < 0.70 else 'check'
    if choice == 'check' or match['benny_balance'] <= 0:
        match['after_benny_check'] = True; match['message'] = 'You check. Benny checks. Your option again: Check or Bet.'; return
    paid = take_benny_bet(match, 'Benny', min(10, match['benny_balance'])); match['to_call'] = paid; match['after_benny_check'] = False; match['message'] = f'You check. Benny bets {paid}. You may Call, Raise, or Fold.'

def benny_response(match, human_bet):
    seen = RANK_VALUE[match['cards'][match['player']]['rank']]; roll = random.random()
    if roll < .12: choice = random.choice(['fold', 'call', 'raise'])
    elif seen >= 11: choice = 'fold' if roll < .75 else 'call'
    elif seen >= 7: choice = 'call'
    else: choice = 'raise' if roll < .55 else 'call'
    if human_bet > match['benny_balance']: choice = 'fold'
    if choice == 'fold': match['benny_folded'] = True; finish_benny(match, match['player'], 'Benny folds. You win the pot!')
    elif choice == 'call': paid = take_benny_bet(match, 'Benny', human_bet); showdown_benny(match, f'Benny calls {paid}.')
    else:
        call_paid = take_benny_bet(match, 'Benny', human_bet); raise_paid = take_benny_bet(match, 'Benny', min(max(10, human_bet), match['benny_balance'])); match['to_call'] = raise_paid; match['message'] = f'Benny automatically calls {call_paid} and raises {raise_paid}. You may Call, Raise, or Fold.'

# ---------------- Two-player mode ----------------
def other_player(match, name):
    return match['players'][1] if match['players'][0] == name else match['players'][0]

def finish_two(match, winner, message, showdown=False):
    match['status'] = 'finished'; match['winner'] = winner; match['message'] = message
    if winner == 'tie':
        p1, p2 = match['players']; half = match['pot'] // 2; match['balances'][p1] += half; match['balances'][p2] += match['pot'] - half; match['result'] = message
    else:
        match['balances'][winner] += match['pot']; match['result'] = message
    for p in match['players']:
        players[p]['balance'] = match['balances'][p]
        players[p]['match_id'] = match['id']

def showdown_two(match, prefix=''):
    p1, p2 = match['players']; v1 = RANK_VALUE[match['cards'][p1]['rank']]; v2 = RANK_VALUE[match['cards'][p2]['rank']]
    if v1 > v2: finish_two(match, p1, prefix + f' {p1} wins the showdown!')
    elif v2 > v1: finish_two(match, p2, prefix + f' {p2} wins the showdown!')
    else: finish_two(match, 'tie', prefix + ' Tie hand. The pot is split.')

def take_two_bet(match, name, amount):
    amount = min(amount, match['balances'][name]); match['balances'][name] -= amount; match['pot'] += amount; return amount

def create_two_match(p1, p2):
    a1, a2 = player_record(p1), player_record(p2)
    if a1['balance'] < ANTE or a2['balance'] < ANTE: return None
    a1['balance'] -= ANTE; a2['balance'] -= ANTE
    c1 = new_card(); c2 = new_card(c1); match_id = secrets.token_hex(6)
    match = {'id': match_id, 'mode': 'two', 'players': [p1, p2], 'cards': {p1: c1, p2: c2}, 'balances': {p1: a1['balance'], p2: a2['balance']}, 'pot': ANTE*2, 'status': 'active', 'winner': None, 'turn': p1, 'to_call': 0, 'last_bettor': None, 'checks': 0, 'message': f'{p1} acts first.', 'result': ''}
    matches[match_id] = match; a1['match_id'] = match_id; a2['match_id'] = match_id
    return match

@app.get('/')
def index():
    name = session.get('player_name'); balance = player_record(name)['balance'] if name else 0
    return page(HOME, name=name, balance=balance)

@app.post('/login')
def login():
    name = request.form.get('name', '').strip()[:30]
    if name: session['player_name'] = name; player_record(name)
    return redirect(url_for('index'))

@app.get('/logout')
def logout():
    global waiting_player
    name = session.get('player_name')
    if waiting_player == name: waiting_player = None
    session.clear(); return redirect(url_for('index'))

@app.post('/play-benny')
def play_benny():
    name = session.get('player_name')
    if not name: return redirect(url_for('index'))
    account = player_record(name)
    if account['balance'] < ANTE: return 'Not enough Cryptinos to ante.', 400
    if account['benny_balance'] < ANTE: return 'Benny does not have enough Cryptinos to ante. You busted Benny!', 400
    account['balance'] -= ANTE; account['benny_balance'] -= ANTE; first = new_card(); match_id = secrets.token_hex(6)
    matches[match_id] = {'id': match_id, 'mode': 'benny', 'player': name, 'cards': {name: first, 'Benny': new_card(first)}, 'player_balance': account['balance'], 'benny_balance': account['benny_balance'], 'pot': ANTE*2, 'status': 'active', 'winner': None, 'to_call': 0, 'benny_folded': False, 'after_benny_check': False, 'message': f'{name} acts first.'}
    account['benny_match_id'] = match_id
    session['match_id'] = match_id; return redirect(url_for('benny_game', match_id=match_id))

@app.get('/game/<match_id>')
def benny_game(match_id):
    match = matches.get(match_id); name = session.get('player_name')
    if not match or match.get('mode') != 'benny' or match['player'] != name: return redirect(url_for('index'))
    return page(BENNY_GAME, match=match, name=name, player_balance=match['player_balance'], benny_balance=match['benny_balance'], symbols=SUIT_SYMBOL)

@app.post('/game/<match_id>/action')
def benny_action(match_id):
    match = matches.get(match_id); name = session.get('player_name')
    if not match or match.get('mode') != 'benny' or match['player'] != name or match['status'] != 'active': return redirect(url_for('index'))
    move = request.form.get('action',''); raw = request.form.get('amount','').strip()
    try: amount = int(raw) if raw else 0
    except ValueError: amount = 0
    if move in ('bet','raise') and amount <= 0: match['message']='Enter a bet or raise amount greater than 0.'; return redirect(url_for('benny_game',match_id=match_id))
    if move == 'fold': finish_benny(match,'Benny','You folded. Benny wins the pot.')
    elif move == 'check':
        if match['to_call']: match['message']=f'You must call {match["to_call"]}, raise, or fold.'
        elif match.get('after_benny_check'): showdown_benny(match,'You check again after Benny checked.')
        else: benny_after_player_check(match)
    elif move == 'call':
        needed=match['to_call']
        if needed <= 0 or needed > match['player_balance']: match['message']='You cannot call that amount.'
        else: take_benny_bet(match,name,needed); match['to_call']=0; showdown_benny(match,f'You call {needed}.')
    elif move in ('bet','raise'):
        required=match['to_call']; total=required+amount
        if total > match['player_balance']: match['message']=f'You only have {match["player_balance"]} Cryptinos available.'
        else:
            paid=take_benny_bet(match,name,total); match['to_call']=0
            if required:
                if amount > match['benny_balance']: match['benny_folded']=True; finish_benny(match,name,'Benny cannot match your raise and folds. You win!')
                else: take_benny_bet(match,'Benny',amount); showdown_benny(match,f'You call {required} and raise {amount}. Benny calls.')
            else: benny_response(match,paid)
    players[name]['balance']=match['player_balance']; return redirect(url_for('benny_game',match_id=match_id))

@app.post('/two/join')
def join_two_player():
    global waiting_player
    name = session.get('player_name')
    if not name: return redirect(url_for('index'))
    account = player_record(name)
    current_id = account.get('match_id'); current = matches.get(current_id) if current_id else None
    if current and current.get('mode') == 'two' and current.get('status') == 'active' and name in current.get('players',[]): return redirect(url_for('two_game', match_id=current_id))
    if account['balance'] < ANTE: return 'Not enough Cryptinos to ante.', 400
    if waiting_player and waiting_player != name:
        opponent = waiting_player
        if player_record(opponent)['balance'] < ANTE: waiting_player = name; return redirect(url_for('waiting_room'))
        waiting_player = None; match = create_two_match(opponent, name); return redirect(url_for('two_game', match_id=match['id']))
    waiting_player = name; return redirect(url_for('waiting_room'))

@app.get('/two/waiting')
def waiting_room():
    name = session.get('player_name')
    if not name: return redirect(url_for('index'))
    match_id = player_record(name).get('match_id'); match = matches.get(match_id) if match_id else None
    if match and match.get('mode') == 'two' and name in match.get('players',[]) and match.get('status') == 'active': return page(WAITING, message='Opponent found. Your match is ready!', match_id=match_id)
    return page(WAITING, message='Waiting for another player to join…', match_id=None)

@app.get('/two/cancel')
def cancel_waiting():
    global waiting_player
    name = session.get('player_name')
    if waiting_player == name: waiting_player = None
    return redirect(url_for('index'))

@app.get('/two/<match_id>')
def two_game(match_id):
    match = matches.get(match_id); name = session.get('player_name')
    if not match or match.get('mode') != 'two' or name not in match.get('players',[]): return redirect(url_for('index'))
    opponent = other_player(match,name)
    return page(TWO_GAME, match=match, name=name, opponent=opponent, my_balance=match['balances'][name], opp_balance=match['balances'][opponent], symbols=SUIT_SYMBOL)

@app.post('/two/<match_id>/action')
def two_action(match_id):
    match = matches.get(match_id); name = session.get('player_name')
    if not match or match.get('mode') != 'two' or name not in match.get('players',[]) or match['status'] != 'active': return redirect(url_for('index'))
    if match['turn'] != name: return redirect(url_for('two_game',match_id=match_id))
    opponent = other_player(match,name); move=request.form.get('action',''); raw=request.form.get('amount','').strip()
    try: amount=int(raw) if raw else 0
    except ValueError: amount=0
    if move in ('bet','raise') and amount <= 0: match['message']='Enter a bet or raise amount greater than 0.'; return redirect(url_for('two_game',match_id=match_id))
    if move == 'fold': finish_two(match,opponent,f'{name} folds. {opponent} wins the pot!')
    elif move == 'check':
        if match['to_call'] > 0: match['message']=f'You must call {match["to_call"]}, raise, or fold.'
        else:
            match['checks'] += 1
            if match['checks'] >= 2: showdown_two(match,f'{name} checks. Both players checked.')
            else: match['turn']=opponent; match['message']=f'{name} checks. {opponent} may Check or Bet.'
    elif move == 'call':
        needed=match['to_call']
        if needed <= 0: match['message']='There is nothing to call.'
        elif needed > match['balances'][name]: match['message']=f'You only have {match["balances"][name]} Cryptinos available.'
        else: take_two_bet(match,name,needed); match['to_call']=0; showdown_two(match,f'{name} calls {needed}.')
    elif move == 'bet':
        if match['to_call'] > 0: match['message']=f'You must call {match["to_call"]}, raise, or fold.'
        elif amount > match['balances'][name]: match['message']=f'You only have {match["balances"][name]} Cryptinos available.'
        else: paid=take_two_bet(match,name,amount); match['checks']=0; match['to_call']=paid; match['last_bettor']=name; match['turn']=opponent; match['message']=f'{name} bets {paid}. {opponent} may Call, Raise, or Fold.'
    elif move == 'raise':
        needed=match['to_call']; total=needed+amount
        if needed <= 0: match['message']='There is no bet to raise.'
        elif total > match['balances'][name]: match['message']=f'You only have {match["balances"][name]} Cryptinos available.'
        else:
            take_two_bet(match,name,total); match['to_call']=amount; match['last_bettor']=name; match['turn']=opponent; match['message']=f'{name} calls {needed} and raises {amount}. {opponent} may Call, Raise, or Fold.'
    return redirect(url_for('two_game',match_id=match_id))

@app.post('/two/<match_id>/rematch')
def rematch(match_id):
    match = matches.get(match_id); name = session.get('player_name')
    if not match or match.get('mode') != 'two' or name not in match.get('players',[]): return redirect(url_for('index'))
    opponent = other_player(match,name)
    if player_record(name)['balance'] < ANTE or player_record(opponent)['balance'] < ANTE: return redirect(url_for('index'))
    new_match = create_two_match(name, opponent)
    return redirect(url_for('two_game',match_id=new_match['id']))

if __name__ == '__main__':
    print('ONI_INVESTOR_TEASER_V2_MULTI is running. Each player name has an independent Benny game. Open http://127.0.0.1:5005')
    print('For another computer on the same Wi-Fi, use this computer\'s local IP address with :5005')
    app.run(host='0.0.0.0', port=5005, debug=False)
