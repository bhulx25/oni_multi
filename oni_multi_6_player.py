from flask import Flask, jsonify, redirect, render_template_string, request, session, url_for
import random
import secrets
import time

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

STARTING_BALANCE = 1000
ANTE = 10
TURN_SECONDS = 45
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANK_VALUE = {rank: value for value, rank in enumerate(RANKS, 2)}
SUIT_SYMBOL = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}

players = {}
matches = {}
tables = {}
waiting_players = set()

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
.table-lobby{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:20px;text-align:left}
.table-list{display:grid;gap:12px;margin:16px 0}
.table-row{display:flex;justify-content:space-between;align-items:center;gap:14px;padding:15px;background:#0a101d;border:1px solid #293752;border-radius:13px}
.table-wrap{max-width:1120px;margin:auto;text-align:center}
.casino-stage{padding:18px;border-radius:28px;background:radial-gradient(circle at 50% 30%,#4a1318 0,#1b070a 48%,#08090f 100%);box-shadow:inset 0 0 70px #000b,0 22px 70px #0009}
.poker-table{position:relative;width:min(760px,94vw);min-height:650px;margin:70px auto 24px;padding:22px;border:12px solid #21160e;border-radius:42px;background:radial-gradient(circle at 50% 38%,#16815a,#075035 72%);box-shadow:inset 0 0 0 4px #d7a63f,inset 0 0 55px #001b12,0 20px 55px #000c,0 0 0 3px #e6bd62;isolation:isolate}
.poker-table:before{content:"ONI";position:absolute;left:50%;top:47%;transform:translate(-50%,-50%);font:900 82px Georgia,serif;letter-spacing:8px;color:#d6ad4f2e;z-index:-1}
.dealer{position:absolute;left:50%;top:-92px;transform:translateX(-50%);display:flex;align-items:center;justify-content:center;gap:10px;width:max-content;max-width:90%;padding:8px 15px;border-radius:22px;background:#07120fe8;border:2px solid #f3c75f99;box-shadow:0 12px 35px #000b}
.dealer img{width:108px;height:108px;border-radius:24px;object-fit:cover;object-position:center 38%;border:3px solid var(--gold);box-shadow:0 0 28px #f3c75f55}
.dealer strong{font-size:22px}
.deck-spread{position:absolute;left:50%;top:64px;transform:translateX(-50%);display:flex;width:340px;height:52px;justify-content:center;z-index:1}
.deck-spread i{display:block;width:34px;height:48px;margin-left:-21px;border:2px solid #fff;border-radius:5px;background:repeating-linear-gradient(45deg,#a4172c 0,#a4172c 5px,#e9b9c0 5px,#e9b9c0 7px);box-shadow:1px 3px 7px #0008;transform:rotate(calc((var(--n) - 9) * 1deg))}
.seats{position:absolute;inset:132px 20px 28px;margin:0}
.seat{position:absolute;width:205px;padding:10px 11px;border-radius:20px;background:linear-gradient(145deg,#251119e8,#090d12ef);border:2px solid #8d6a36;min-height:100px;box-shadow:0 12px 24px #0009;text-align:left}
.seat:nth-child(1){left:-72px;top:0}.seat:nth-child(2){right:-72px;top:0}
.seat:nth-child(3){left:-98px;top:42%}.seat:nth-child(4){right:-98px;top:42%}
.seat:nth-child(5){left:12px;bottom:-26px}.seat:nth-child(6){right:12px;bottom:-26px}
.seat-avatar{float:left;width:54px;height:54px;margin-right:9px;border-radius:50%;display:grid;place-items:center;font-size:30px;background:linear-gradient(145deg,#1d9ab2,#f3c75f);border:3px solid #ffe49a;box-shadow:0 0 18px #f3c75f44}
.seat:nth-child(even) .seat-avatar{background:linear-gradient(145deg,#b52b55,#f3c75f)}
.seat-card{position:absolute;right:9px;bottom:8px;width:31px;height:43px;border:2px solid white;border-radius:5px;background:repeating-linear-gradient(45deg,#a4172c 0,#a4172c 5px,#e9b9c0 5px,#e9b9c0 7px);box-shadow:1px 3px 8px #0008}
.seat.turn{border:2px solid var(--gold);box-shadow:0 0 18px #f3c75f88}
.seat.turn:after{content:"???";position:absolute;left:26px;top:-42px;padding:6px 12px;border:3px solid #1a1420;border-radius:50% 50% 46% 54%;background:#fff;color:#7b1ee6;font:900 24px/1 "Comic Sans MS","Trebuchet MS",cursive;letter-spacing:2px;text-shadow:1px 1px 0 #f4d8ff;box-shadow:0 5px 0 #1a1420,0 10px 20px #0008;transform:rotate(-7deg);z-index:8;animation:questionRefresh 2s ease-in-out infinite}
.seat.turn:before{content:"";position:absolute;left:50px;top:-10px;width:11px;height:11px;border:3px solid #1a1420;border-radius:50%;background:#fff;z-index:8;animation:questionRefresh 2s ease-in-out infinite}
.seat.turn.choice-made:after,.seat.turn.choice-made:before{display:none}
@keyframes questionRefresh{0%,48%{opacity:1;transform:translateY(0) rotate(-7deg) scale(1)}58%,88%{opacity:0;transform:translateY(-8px) rotate(5deg) scale(.78)}100%{opacity:1;transform:translateY(0) rotate(-7deg) scale(1)}}
.seat.folded{opacity:.5}
.seat.paused{opacity:.62;border-style:dashed}
.seat-name{font-weight:800}.seat-bank{color:#bff5df;font-size:13px;margin-top:4px}
.table-pot{position:absolute;left:50%;top:31%;transform:translate(-50%,-50%);padding:9px 18px;border:2px solid #d7a63f;border-radius:13px;background:#080b10e8;color:#ffe49a;font-size:24px;font-weight:900;box-shadow:0 7px 22px #0009}
.pot-balance{position:absolute;right:18px;bottom:16px;padding:8px 12px;border:1px solid #d7a63f;border-radius:12px;background:#080b10e8;color:#ffe49a;font-weight:800;font-size:13px}
.duel-table{min-height:570px;margin-top:78px}
.duel-benny{position:absolute;left:50%;top:-96px;transform:translateX(-50%);display:flex;align-items:center;gap:12px;padding:8px 15px;border-radius:22px;background:#07120fee;border:2px solid #f3c75f99;box-shadow:0 12px 35px #000b}
.duel-benny img{width:118px;height:118px;border-radius:24px;object-fit:cover;object-position:center 38%;border:3px solid var(--gold)}
.duel-benny-card{width:62px;height:88px;margin:0;font-size:19px;border-radius:8px}
.duel-player{position:absolute;left:50%;bottom:-35px;transform:translateX(-50%);width:250px;padding:12px;border-radius:24px;background:linear-gradient(145deg,#263b52,#111723);border:2px solid #f3c75f;box-shadow:0 14px 28px #000b}
.duel-avatar{width:72px;height:72px;margin:auto;border-radius:50%;display:grid;place-items:center;font-size:42px;background:linear-gradient(145deg,#1d9ab2,#f3c75f);border:3px solid #ffe49a}
.face-down-card{width:72px;height:100px;margin:8px auto 0;border:3px solid white;border-radius:9px;background:repeating-linear-gradient(45deg,#a4172c 0,#a4172c 7px,#e9b9c0 7px,#e9b9c0 10px);box-shadow:2px 5px 14px #0009}
.game-actions{margin-top:42px}
.poker-table.head-table{width:min(600px,88vw);min-height:390px;margin:58px auto 14px;padding:14px;border-width:9px;border-radius:34px}
.head-table:before{top:48%;font-size:62px}
.head-table .dealer{top:-70px;padding:6px 12px}
.head-table .dealer img{width:76px;height:76px;border-radius:18px}
.head-table .dealer strong{font-size:18px}
.head-table .deck-spread{top:32px;width:230px;transform:translateX(-50%) scale(.82)}
.head-table .seats{inset:74px 12px 16px}
.head-table .seat{width:178px;min-height:84px;padding:8px 9px;border-radius:16px}
.head-table .seat:nth-child(1){left:-38px;top:42%}
.head-table .seat:nth-child(2){right:-38px;top:42%}
.head-table .seat-avatar{width:44px;height:44px;font-size:25px}
.head-table .seat-card{width:27px;height:37px}
.head-table .table-pot{top:45%;padding:7px 14px;font-size:18px}
.head-table .pot-balance{right:10px;bottom:8px;padding:6px 9px;font-size:11px}
.table-wrap>h1{font-size:clamp(28px,5vw,40px)!important;margin-top:7px!important}
.action-dock{max-width:650px;margin:10px auto 12px;padding:10px 14px;border:2px solid #d7a63f;border-radius:16px;background:#090e19;box-shadow:0 12px 28px #0008}
.action-title{color:var(--gold2);font-weight:900;letter-spacing:1.5px}
.action-dock .actions{margin-top:8px}
.action-dock button{min-width:104px;padding:10px 16px}
button:disabled{cursor:not-allowed;opacity:.42;filter:none}
.holder{max-width:930px;margin:18px auto;padding:16px;border-radius:20px;background:linear-gradient(#4b2d18,#251308);border:3px solid #8a5a2d;box-shadow:inset 0 0 18px #000c}
.holder.open{position:fixed;left:50%;bottom:12px;transform:translateX(-50%);width:min(930px,96vw);max-height:58vh;overflow:auto;z-index:9000;box-shadow:0 20px 70px #000,inset 0 0 18px #000c}
.holder-cards{display:flex;gap:10px;justify-content:center;align-items:flex-end;flex-wrap:wrap;filter:brightness(0);transition:.15s}
.holder.open .holder-cards{filter:none}
.mini-card{width:108px;height:150px;margin:4px;display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:10px;background:white;color:#111;font-size:20px;font-weight:800;box-shadow:2px 4px 12px #0008}
.mini-card.red{color:#c7192d}.mini-card.folded-card{opacity:.45}
.card-label{font-size:12px;color:#fff;background:#000b;padding:4px 7px;border-radius:7px;margin-bottom:5px}
.own-card{background:repeating-linear-gradient(45deg,#142b62,#142b62 8px,#f3c75f 8px,#f3c75f 11px);color:#fff;text-shadow:0 2px 3px #000}
.code{font-size:28px;letter-spacing:5px;color:var(--gold2);font-weight:900}
.red{color:#c7192d}
.pot{font-size:26px;color:var(--gold)}
.message{min-height:28px;font-size:19px;margin:14px}
.note{font-size:14px;color:var(--muted)}
.waiting{font-size:22px;padding:18px;background:#0a101d;border-radius:12px;margin:18px 0}
.turn-clock{display:inline-block;min-width:145px;margin:4px auto 12px;padding:8px 14px;border:1px solid #d7a63f;border-radius:999px;background:#080b10e8;color:#ffe49a;font-weight:900}
.turn-clock.urgent{background:#6f1726;color:white;animation:clockPulse .8s infinite alternate}
@keyframes clockPulse{to{transform:scale(1.04)}}
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
  .table-lobby{grid-template-columns:1fr}
  .casino-stage{padding:10px}.poker-table{width:94vw;min-height:720px;margin-top:82px}.seats{inset:125px 8px 30px}
  .seat{width:46%;min-height:92px}.seat:nth-child(1){left:0}.seat:nth-child(2){right:0}.seat:nth-child(3){left:0}.seat:nth-child(4){right:0}.seat:nth-child(5){left:0;bottom:0}.seat:nth-child(6){right:0;bottom:0}
  .deck-spread{width:260px}.duel-table{min-height:570px}
  .poker-table.head-table{width:min(600px,90vw);min-height:400px;margin-top:66px}
  .head-table .seats{inset:74px 8px 14px}
  .head-table .seat{width:43%;min-height:82px}
  .head-table .seat:nth-child(1){left:-12px;top:43%}.head-table .seat:nth-child(2){right:-12px;top:43%}
  .holder{padding:11px;margin:10px auto}.mini-card{width:82px;height:114px}
}
@media(max-width:520px){
  .vision{grid-template-columns:1fr}.site{padding:10px}.shell{padding:18px 0}
  .poker-table.head-table{width:92vw;min-height:350px;margin-top:60px;border-width:7px}
  .head-table .dealer{top:-61px}.head-table .dealer img{width:62px;height:62px}
  .head-table .deck-spread{top:25px;transform:translateX(-50%) scale(.66)}
  .head-table .seats{inset:62px 5px 10px}.head-table .seat{width:45%;min-height:78px;padding:7px;font-size:13px}
  .head-table .seat:nth-child(1){left:-8px;top:43%}.head-table .seat:nth-child(2){right:-8px;top:43%}
  .head-table .seat-avatar{width:38px;height:38px;font-size:21px}.head-table .seat-bank{font-size:11px}
  .head-table .table-pot{font-size:15px;padding:6px 10px}.action-dock{padding:9px}
  .action-dock button{min-width:86px;padding:9px 11px;font-size:15px}
  .message{font-size:16px;margin:9px}.turn-clock{margin-bottom:7px;padding:6px 11px}
}
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
  <div class="eyebrow">ONI MULTI • Benny deals every table</div>
  <h1>ONI</h1>
  <p class="lead">One card. Hidden information. Fast decisions. ONI is the teaser for a multi-game competitive casino platform built around Cryptinos.</p>
  <div class="badges">
    <span class="badge">Fast-play poker</span>
    <span class="badge">Computer opponent</span>
    <span class="badge">2–6 human players</span>
    <span class="badge">Three clear play environments</span>
  </div>
  {% if name %}
    <div class="balance-pill">{{ name }} • {{ balance }} Cryptinos</div>
    <div class="actions">
      <form method="post" action="{{ url_for('play_benny') }}"><button>Play Benny</button></form>
      <a class="button secondary" href="{{ url_for('table_lobby', mode='head_to_head') }}">Head-to-Head</a>
      <a class="button secondary" href="{{ url_for('table_lobby', mode='multi') }}">Multi Table</a>
    </div>
    {% if balance < 10 %}<form method="post" action="{{ url_for('buy_cryptinos') }}" style="margin-top:14px"><button>Buy 1,000 Test Cryptinos</button></form><p class="note">Prototype refill only—no real payment is processed.</p>{% endif %}
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
  <img src="/static/benny_raised.png" alt="Benny computer opponent" style="width:180px;height:180px;border-radius:24px;object-fit:cover;border:4px solid #f3c75f;box-shadow:0 0 40px #f3c75f33">
  <h2 style="margin-bottom:5px">Meet Benny</h2>
  <p class="kicker">ONI's computer avatar. He checks, bets, raises, folds—and occasionally bluffs.</p>
  <div class="balance-pill">Computer Opponent • Ready</div>
</div>
</section>

<div class="game-grid">
  <div class="game-card">
    <div class="oni-icon">♠</div><h3>ONI</h3>
    <p>The launch game: see every opponent's card, but never your own until the hand ends.</p>
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

BENNY_GAME = '''<div class="box" style="max-width:1080px">
<div class="eyebrow">COMPUTER OPPONENT</div>
<h1 style="font-size:48px">ONI — PLAY BENNY</h1>
<p class="note">You can see Benny's card—but not your own.</p>
<div class="casino-stage">
<div class="poker-table duel-table">
  <div class="duel-benny">
    <img src="/static/benny_raised.png" alt="Benny computer opponent">
    <div><strong style="display:block;color:#ffe49a;font-size:23px">BENNY</strong><span class="note">{{ benny_balance }} Cryptinos</span></div>
    <div class="card duel-benny-card {% if match.cards.Benny.suit in ['Hearts','Diamonds'] %}red{% endif %}">{{ match.cards.Benny.rank }}<br>{{ symbols[match.cards.Benny.suit] }}</div>
  </div>
  <div class="deck-spread" aria-label="Undealt cards">{% for n in range(18) %}<i style="--n:{{ n }}"></i>{% endfor %}</div>
  <div class="table-pot">POT<br>{{ match.pot }}</div>
  <div class="duel-player">
    <div class="duel-avatar" aria-hidden="true">😎</div>
    <strong>{{ name }}</strong><div class="seat-bank">{{ player_balance }} Cryptinos</div>
    <div class="face-down-card" aria-label="Your hidden card"></div>
  </div>
  <div class="pot-balance">POT BALANCE<br>{{ match.pot }}</div>
</div>
</div>
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

TABLE_LOBBY = '''<div class="box">
<div class="eyebrow">ONI {{ 'HEAD-TO-HEAD' if lobby_mode == 'head_to_head' else 'MULTI TABLE' }} LOBBY</div><h1 style="font-size:52px">Choose a Table</h1>
<p class="lead" style="margin:auto">{{ 'Two human players at one table.' if lobby_mode == 'head_to_head' else 'Two players may start, and up to six can join.' }} Benny deals but never takes a seat.</p>
{% if assigned_table %}<div class="waiting">You have a table invitation. <a class="button" href="{{ url_for('multi_table', table_id=assigned_table) }}">Go to My Table</a></div>{% endif %}
<div class="table-lobby">
  <div class="game-card"><h2>Create {{ 'a Head-to-Head' if lobby_mode == 'head_to_head' else 'a Multi Table' }}</h2>
    <form method="post" action="{{ url_for('create_table') }}">
      <p><input name="table_name" maxlength="30" placeholder="Table name" required></p>
      <input type="hidden" name="mode" value="{{ lobby_mode }}">
      <button>Create Table</button>
    </form>
  </div>
  <div class="game-card"><h2>Waiting for an invitation</h2>
    <p>Put your name on the waiting list so a seated player can invite you.</p>
    <form method="post" action="{{ url_for('toggle_waiting') }}"><input type="hidden" name="mode" value="{{ lobby_mode }}"><button class="secondary">{{ 'Leave Waiting List' if on_waiting_list else 'Join Waiting List' }}</button></form>
    {% if error %}<p style="color:#ffd5dc">{{ error }}</p>{% endif %}
  </div>
</div>
<h2 style="margin-top:28px">Open tables</h2>
<div class="table-list">
{% for table in open_tables %}
  <div class="table-row"><div><b>{{ table.name }}</b><div class="note">{{ table.players|length }}/{{ table.max_players }} players • {{ table.status|title }}</div></div>
  <form method="post" action="{{ url_for('join_table', table_id=table.id) }}"><button {% if table.players|length >= table.max_players %}disabled{% endif %}>Join</button></form></div>
{% else %}<div class="waiting">No open tables yet. Create the first one.</div>{% endfor %}
</div>
<div class="actions"><a class="button secondary" href="{{ url_for('table_lobby', mode='head_to_head' if lobby_mode == 'multi' else 'multi') }}">Switch to {{ 'Head-to-Head' if lobby_mode == 'multi' else 'Multi Table' }}</a><a class="button secondary" href="{{ url_for('index') }}">Casino Lobby</a></div></div>'''

MULTI_TABLE = '''<div class="table-wrap">
<div class="eyebrow">{{ 'HEAD-TO-HEAD' if table.mode == 'head_to_head' else 'MULTI' }} TABLE • {{ table.players|length }}/{{ table.max_players }} PLAYERS</div>
<h1 style="font-size:44px;margin-bottom:6px">{{ table.name }}</h1>
<div class="casino-stage">
<div class="poker-table {% if table.mode == 'head_to_head' %}head-table{% endif %}">
  <div class="dealer"><img src="/static/benny_raised.png" alt="Benny"><div><strong style="color:#ffe49a">BENNY</strong><div class="note">Dealer only</div></div></div>
  <div class="deck-spread" aria-label="Undealt cards">{% for n in range(18) %}<i style="--n:{{ n }}"></i>{% endfor %}</div>
  <div class="seats">
  {% for seat in seats %}<div class="seat {% if seat.turn %}turn{% endif %} {% if seat.folded %}folded{% endif %} {% if seat.paused %}paused{% endif %}">
    <div class="seat-avatar" aria-hidden="true">{{ ['😎','🤠','🧠','🔥','🦊','🎯'][loop.index0] }}</div>
    <div class="seat-name">Seat {{ loop.index }} • {{ seat.name }}</div><div class="seat-bank">{{ seat.balance }} Cryptinos{% if seat.paused %} • PAUSED{% elif seat.waiting %} • NEXT HAND{% elif seat.folded %} • FOLDED{% elif seat.all_in %} • ALL-IN{% endif %}</div>
    {% if hand and not seat.waiting %}<div class="seat-card" aria-label="Dealt card"></div>{% endif %}
  </div>{% endfor %}
  {% for n in range(table.max_players-seats|length) %}<div class="seat"><div class="seat-avatar" aria-hidden="true">＋</div><div class="seat-name">Open Seat</div><div class="seat-bank">Waiting for a player</div></div>{% endfor %}
  </div>
  {% if hand %}<div class="table-pot">POT<br>{{ hand.pot }}</div><div class="pot-balance">POT BALANCE<br>{{ hand.pot }}</div>{% endif %}
</div>
</div>
<div class="message">{{ message }}</div>
{% if table.status == 'active' and hand.turn %}<div class="turn-clock" id="turnClock" data-deadline="{{ hand.turn_deadline }}">{{ hand.turn }}: <span>--</span> seconds</div>{% endif %}

{% if table.status == 'waiting' %}
  {% if name == table.creator and active_seat_count >= 2 %}<form method="post" action="{{ url_for('start_table_hand', table_id=table.id) }}"><button>Ask Benny to Deal</button></form>{% else %}<div class="waiting">Waiting for {{ table.creator or 'a player' }} to start when at least two active players are seated.</div>{% endif %}
{% elif table.status == 'active' and hand.turn == name %}
  <div class="action-dock"><div class="action-title">YOUR MOVE</div>
  <form id="multiActionForm" method="post" action="{{ url_for('multi_action', table_id=table.id) }}"><input type="hidden" name="action" id="multiAction"><input type="hidden" name="amount" id="multiAmount"><div class="actions">
  {% if to_call > 0 %}<button type="button" onclick="multiSimple('call')">{{ 'Call All-In '+my_balance|string if my_balance < to_call else 'Call '+to_call|string }}</button>{% if my_balance > to_call %}<button type="button" onclick="multiAsk('raise')">Raise</button>{% endif %}
  {% else %}<button type="button" onclick="multiSimple('check')">{% if hand.double_check_phase and hand.opener == name %}Double Check{% else %}Check{% endif %}</button>{% if my_balance > 0 %}<button type="button" onclick="multiAsk('bet')">Bet</button>{% endif %}{% endif %}
  <button type="button" class="danger" onclick="multiSimple('fold')">Fold</button></div></form></div>
  <script>
  function clearTurnQuestions(){const active=document.querySelector('.seat.turn');if(active)active.classList.add('choice-made')}
  function multiSimple(a){clearTurnQuestions();document.getElementById('multiAction').value=a;document.getElementById('multiAmount').value='';document.getElementById('multiActionForm').submit()}
  function multiAsk(a){const due={{ to_call|int }},bal={{ my_balance|int }},max=a==='raise'?bal-due:bal,label=a==='raise'?'Raise by how much?':'Bet how much?';const v=prompt(label+'\\nMaximum: '+max);if(v===null)return;const n=Number(v);if(!Number.isInteger(n)||n<=0||n>max){alert('Enter a whole number from 1 to '+max);return}clearTurnQuestions();document.getElementById('multiAction').value=a;document.getElementById('multiAmount').value=String(n);document.getElementById('multiActionForm').submit()}
  </script>
{% elif table.status == 'active' %}<div class="action-dock"><div class="action-title">{{ hand.turn }}'S MOVE</div><div class="actions">{% if to_call > 0 %}<button type="button" disabled>Call</button><button type="button" disabled>Raise</button>{% else %}<button type="button" disabled>Check</button><button type="button" disabled>Bet</button>{% endif %}<button type="button" class="danger" disabled>Fold</button></div><div class="note">Your controls activate automatically when it is your turn.</div></div>
{% elif table.status == 'finished' %}
  <h3>{{ hand.result }}</h3>{% if in_hand %}<h3>Your hidden card was:</h3><div class="card {% if my_card.suit in ['Hearts','Diamonds'] %}red{% endif %}">{{ my_card.rank }}<br>{{ symbols[my_card.suit] }}</div>{% else %}<div class="waiting">You joined during the last hand and will be dealt into the next one.</div>{% endif %}
  {% if name == table.creator %}<form method="post" action="{{ url_for('next_table_hand', table_id=table.id) }}"><button>Deal Next Hand</button></form>{% else %}<div class="waiting">Waiting for {{ table.creator }} to deal the next hand.</div>{% endif %}
{% endif %}
{% if hand and in_hand %}
<div class="holder" id="cardHolder">
  <button type="button" id="holderButton" class="secondary" aria-expanded="false" onclick="toggleHolder()">LOOK AT THE OTHER CARDS</button>
  <p class="note">Your own card always stays hidden during the hand.</p>
  <div class="holder-cards" aria-hidden="true">
    <div><div class="card-label">YOUR CARD</div><div class="mini-card own-card">ONI</div></div>
    {% for item in visible_cards %}<div><div class="card-label">{{ item.name }}</div><div class="mini-card {% if item.card.suit in ['Hearts','Diamonds'] %}red{% endif %} {% if item.folded %}folded-card{% endif %}">{{ item.card.rank }}<br>{{ symbols[item.card.suit] }}</div></div>{% endfor %}
  </div>
</div>
<script>
const holderKey='oni-holder-{{ table.id }}-{{ name }}';
function setHolder(open){const h=document.getElementById('cardHolder'),b=document.getElementById('holderButton');h.classList.toggle('open',open);b.textContent=open?'CLOSE CARD HOLDER':'LOOK AT THE OTHER CARDS';b.setAttribute('aria-expanded',String(open));h.querySelector('.holder-cards').setAttribute('aria-hidden',String(!open));localStorage.setItem(holderKey,open?'open':'closed')}
function toggleHolder(){setHolder(!document.getElementById('cardHolder').classList.contains('open'))}
if(localStorage.getItem(holderKey)==='open')setHolder(true);
</script>
{% endif %}
{% if waiting_names %}<div class="game-card" style="margin-top:18px"><h2>Waiting players</h2><div class="actions">{% for waiting_name in waiting_names %}<form method="post" action="{{ url_for('invite_player', table_id=table.id) }}"><input type="hidden" name="player" value="{{ waiting_name }}"><button class="secondary">Invite {{ waiting_name }}</button></form>{% endfor %}</div></div>{% endif %}
<div class="actions" style="margin-top:18px"><a class="button secondary" href="{{ url_for('table_lobby', mode=table.mode) }}">Table Lobby</a><form method="post" action="{{ url_for('toggle_pause', table_id=table.id) }}"><button class="secondary">{{ 'Resume My Seat' if my_paused else 'Pause My Seat' }}</button></form><form method="post" action="{{ url_for('leave_table', table_id=table.id) }}"><button class="danger">Leave Table</button></form></div>
<script>
const initialVersion={{ table.version|int }};
let navigating=false;
async function quietTableCheck(){if(navigating)return;try{const r=await fetch('{{ url_for('table_state', table_id=table.id) }}',{cache:'no-store'});if(!r.ok)return;const s=await r.json();if(s.version!==initialVersion){navigating=true;location.reload();}}catch(e){}}
setInterval(quietTableCheck,1200);
const clock=document.getElementById('turnClock');
if(clock){const tick=()=>{const left=Math.max(0,Math.ceil(Number(clock.dataset.deadline)-Date.now()/1000));clock.querySelector('span').textContent=left;clock.classList.toggle('urgent',left<=10);if(left===0)quietTableCheck()};tick();setInterval(tick,500)}
</script>
</div>'''

def new_card(exclude=None):
    while True:
        card = {'rank': random.choice(RANKS), 'suit': random.choice(SUITS)}
        if card != exclude:
            return card

def player_record(name):
    account = players.setdefault(name, {'balance': STARTING_BALANCE, 'benny_balance': STARTING_BALANCE, 'match_id': None, 'benny_match_id': None, 'table_id': None, 'paused': False})
    account.setdefault('benny_balance', STARTING_BALANCE)
    account.setdefault('match_id', None)
    account.setdefault('benny_match_id', None)
    account.setdefault('table_id', None)
    account.setdefault('paused', False)
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
    if seen == RANK_VALUE['Ace']:
        # Benny can never beat the Ace he sees. His only aggressive move is a bluff raise.
        choice = 'raise' if roll < .12 else 'fold'
    elif roll < .12: choice = random.choice(['fold', 'call', 'raise'])
    elif seen >= 11: choice = 'fold' if roll < .75 else 'call'
    elif seen >= 7: choice = 'call'
    else: choice = 'raise' if roll < .55 else 'call'
    if human_bet > match['benny_balance']: choice = 'fold'
    if choice == 'fold': match['benny_folded'] = True; finish_benny(match, match['player'], 'Benny folds. You win the pot!')
    elif choice == 'call': paid = take_benny_bet(match, 'Benny', human_bet); showdown_benny(match, f'Benny calls {paid}.')
    else:
        call_paid = take_benny_bet(match, 'Benny', human_bet); raise_paid = take_benny_bet(match, 'Benny', min(max(10, human_bet), match['benny_balance'])); match['to_call'] = raise_paid; match['message'] = f'Benny automatically calls {call_paid} and raises {raise_paid}. You may Call, Raise, or Fold.'

# ---------------- 2–6 player tables; Benny is the dealer only ----------------
def bump_table(table):
    table['version'] = table.get('version', 0) + 1

def set_multi_turn(hand, name):
    hand['turn'] = name
    hand['turn_deadline'] = time.time() + TURN_SECONDS if name else 0

def create_multi_table(creator, table_name, mode):
    table_id = secrets.token_hex(5)
    mode = 'head_to_head' if mode == 'head_to_head' else 'multi'
    table = {
        'id': table_id, 'name': table_name, 'mode': mode,
        'max_players': 2 if mode == 'head_to_head' else 6,
        'creator': creator, 'players': [creator], 'status': 'waiting',
        'hand': None, 'first_actor_index': 0, 'version': 1,
    }
    tables[table_id] = table
    player_record(creator)['table_id'] = table_id
    return table

def join_multi_table(table, name):
    if name not in table['players'] and len(table['players']) < table['max_players']:
        table['players'].append(name)
        if not table.get('creator'):
            table['creator'] = name
        bump_table(table)
    player_record(name)['table_id'] = table['id']
    waiting_players.discard(name)

def sync_multi_balances(hand):
    for name, balance in hand['balances'].items():
        player_record(name)['balance'] = balance

def active_multi_players(hand):
    return [p for p in hand['order'] if p not in hand['folded']]

def next_multi_turn(hand, after_name):
    order = hand['order']
    start = order.index(after_name)
    for offset in range(1, len(order) + 1):
        candidate = order[(start + offset) % len(order)]
        if candidate in hand['pending'] and candidate not in hand['folded'] and hand['balances'][candidate] > 0:
            return candidate
    return None

def award_and_finish(table, hand, awards, message):
    for player, amount in awards.items():
        hand['balances'][player] += amount
    sync_multi_balances(hand)
    set_multi_turn(hand, None)
    hand['result'] = message
    hand['message'] = message
    table['status'] = 'finished'
    bump_table(table)

def finish_multi_by_fold(table, hand):
    winner = active_multi_players(hand)[0]
    award_and_finish(table, hand, {winner: hand['pot']}, f'{winner} wins {hand["pot"]} Cryptinos. Everyone else folded.')

def showdown_multi(table, hand):
    active = active_multi_players(hand)
    awards = {p: 0 for p in active}
    levels = sorted({amount for amount in hand['contributions'].values() if amount > 0})
    previous = 0
    for level in levels:
        contributors = [p for p, amount in hand['contributions'].items() if amount >= level]
        side_pot = (level - previous) * len(contributors)
        eligible = [p for p in active if hand['contributions'][p] >= level]
        if eligible and side_pot:
            best = max(RANK_VALUE[hand['cards'][p]['rank']] for p in eligible)
            winners = [p for p in eligible if RANK_VALUE[hand['cards'][p]['rank']] == best]
            share, remainder = divmod(side_pot, len(winners))
            for index, winner in enumerate(winners):
                awards[winner] += share + (1 if index < remainder else 0)
        previous = level
    summary = ', '.join(f'{p} wins {amount}' for p, amount in awards.items() if amount)
    award_and_finish(table, hand, awards, 'Showdown: ' + summary + ' Cryptinos.')

def start_multi_hand(table):
    order = [p for p in table['players'] if player_record(p)['balance'] >= ANTE and not player_record(p)['paused']]
    if len(order) < 2:
        return False
    deck = [{'rank': rank, 'suit': suit} for suit in SUITS for rank in RANKS]
    random.shuffle(deck)
    first_index = table['first_actor_index'] % len(order)
    table['first_actor_index'] = (first_index + 1) % len(order)
    for player in order:
        players[player]['balance'] -= ANTE
    rotated = order[first_index:] + order[:first_index]
    first = next((p for p in rotated if players[p]['balance'] > 0), rotated[0])
    hand = {
        'order': order, 'cards': {p: deck.pop() for p in order},
        'balances': {p: players[p]['balance'] for p in order},
        'contributions': {p: ANTE for p in order}, 'committed': {p: 0 for p in order},
        'folded': set(), 'pending': {p for p in order if players[p]['balance'] > 0},
        'current_bet': 0, 'pot': ANTE * len(order), 'turn': first,
        'turn_deadline': time.time() + TURN_SECONDS,
        'opener': first, 'double_check_phase': False,
        'message': f'Benny deals. {first} acts first.', 'result': '',
    }
    table['hand'] = hand
    table['status'] = 'active'
    bump_table(table)
    if not hand['pending']:
        showdown_multi(table, hand)
    return True

def take_multi_chips(hand, name, amount):
    paid = min(amount, hand['balances'][name])
    hand['balances'][name] -= paid
    hand['committed'][name] += paid
    hand['contributions'][name] += paid
    hand['pot'] += paid
    sync_multi_balances(hand)
    return paid

def clean_multi_pending(hand):
    hand['pending'] = {
        p for p in hand['pending']
        if p not in hand['folded'] and hand['balances'][p] > 0
    }

def advance_multi_after_action(table, hand, actor):
    if len(active_multi_players(hand)) == 1:
        finish_multi_by_fold(table, hand)
        return
    clean_multi_pending(hand)
    if not hand['pending']:
        opener_can_double_check = (
            hand['current_bet'] == 0 and not hand['double_check_phase']
            and hand['opener'] in active_multi_players(hand)
            and hand['balances'][hand['opener']] > 0
        )
        if opener_can_double_check:
            hand['double_check_phase'] = True
            hand['pending'] = {hand['opener']}
            set_multi_turn(hand, hand['opener'])
            hand['message'] = f'Everyone checked. Only {hand["opener"]}, the first player, may Double Check or Bet.'
            bump_table(table)
        else:
            showdown_multi(table, hand)
    else:
        next_player = next_multi_turn(hand, actor)
        set_multi_turn(hand, next_player)
        hand['message'] += f' {next_player} acts next.'
        bump_table(table)

def expire_multi_turn(table):
    hand = table.get('hand')
    if not hand or table.get('status') != 'active' or not hand.get('turn'):
        return False
    if time.time() < hand.get('turn_deadline', 0):
        return False
    name = hand['turn']
    due = max(0, hand['current_bet'] - hand['committed'][name])
    if due:
        hand['folded'].add(name)
        hand['pending'].discard(name)
        hand['message'] = f'{name} ran out of time and automatically folds.'
    else:
        hand['pending'].discard(name)
        hand['message'] = f'{name} ran out of time and automatically checks.'
    advance_multi_after_action(table, hand, name)
    return True

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
    session.clear(); return redirect(url_for('index'))

@app.post('/buy-cryptinos')
def buy_cryptinos():
    name = session.get('player_name')
    if not name:
        return redirect(url_for('index'))
    player_record(name)['balance'] += 1000
    return redirect(url_for('index'))

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

@app.get('/tables')
def table_lobby():
    name = session.get('player_name')
    if not name:
        return redirect(url_for('index'))
    lobby_mode = 'head_to_head' if request.args.get('mode') == 'head_to_head' else 'multi'
    open_tables = [t for t in tables.values() if t['mode'] == lobby_mode and len(t['players']) < t['max_players']]
    assigned = player_record(name).get('table_id')
    return page(TABLE_LOBBY, open_tables=open_tables, lobby_mode=lobby_mode,
                on_waiting_list=name in waiting_players, assigned_table=assigned,
                error=request.args.get('error', ''))

@app.post('/tables/create')
def create_table():
    name = session.get('player_name')
    if not name:
        return redirect(url_for('index'))
    table_name = request.form.get('table_name', '').strip()[:30] or f"{name}'s Table"
    mode = 'head_to_head' if request.form.get('mode') == 'head_to_head' else 'multi'
    table = create_multi_table(name, table_name, mode)
    return redirect(url_for('multi_table', table_id=table['id']))

@app.post('/tables/<table_id>/join')
def join_table(table_id):
    name = session.get('player_name')
    table = tables.get(table_id)
    if not name or not table:
        return redirect(url_for('table_lobby'))
    if len(table['players']) >= table['max_players'] and name not in table['players']:
        return redirect(url_for('table_lobby', mode=table['mode'], error='That table is full.'))
    join_multi_table(table, name)
    return redirect(url_for('multi_table', table_id=table_id))

@app.post('/waiting/toggle')
def toggle_waiting():
    name = session.get('player_name')
    if not name:
        return redirect(url_for('index'))
    if name in waiting_players:
        waiting_players.discard(name)
    else:
        waiting_players.add(name)
    return redirect(url_for('table_lobby', mode=request.form.get('mode', 'multi')))

@app.post('/table/<table_id>/invite')
def invite_player(table_id):
    name = session.get('player_name')
    target = request.form.get('player', '').strip()
    table = tables.get(table_id)
    if name in (table or {}).get('players', []) and target in waiting_players and len(table['players']) < table['max_players']:
        join_multi_table(table, target)
    return redirect(url_for('multi_table', table_id=table_id))

@app.get('/table/<table_id>')
def multi_table(table_id):
    name = session.get('player_name')
    table = tables.get(table_id)
    if not name or not table or name not in table['players']:
        return redirect(url_for('table_lobby', mode=table['mode'] if table else 'multi'))
    expire_multi_turn(table)
    hand = table.get('hand')
    in_hand = bool(hand and name in hand['order'])
    visible_cards = []
    if in_hand:
        visible_cards = [
            {'name': p, 'card': hand['cards'][p], 'folded': p in hand['folded']}
            for p in hand['order'] if p != name
        ]
    seats = []
    for player in table['players']:
        seats.append({
            'name': player,
            'balance': hand['balances'].get(player, player_record(player)['balance']) if hand else player_record(player)['balance'],
            'turn': bool(hand and hand.get('turn') == player),
            'folded': bool(hand and player in hand['order'] and player in hand['folded']),
            'all_in': bool(hand and player in hand['order'] and hand['balances'][player] == 0),
            'waiting': bool(hand and player not in hand['order']),
            'paused': player_record(player)['paused'],
        })
    my_balance = hand['balances'][name] if in_hand else player_record(name)['balance']
    to_call = max(0, hand['current_bet'] - hand['committed'][name]) if in_hand and table['status'] == 'active' else 0
    my_card = hand['cards'][name] if in_hand and table['status'] == 'finished' else None
    message = hand['message'] if hand else 'Benny is ready to deal when at least two players are seated.'
    waiting_names = sorted(p for p in waiting_players if p not in table['players'])
    active_seat_count = sum(not player_record(p)['paused'] and player_record(p)['balance'] >= ANTE for p in table['players'])
    return page(MULTI_TABLE, table=table, hand=hand, in_hand=in_hand, name=name,
                seats=seats, visible_cards=visible_cards, symbols=SUIT_SYMBOL,
                my_balance=my_balance, to_call=to_call, my_card=my_card, message=message,
                waiting_names=waiting_names, my_paused=player_record(name)['paused'],
                active_seat_count=active_seat_count)

@app.get('/table/<table_id>/state')
def table_state(table_id):
    name = session.get('player_name')
    table = tables.get(table_id)
    if not table or name not in table['players']:
        return jsonify({'gone': True, 'version': -1}), 404
    expire_multi_turn(table)
    return jsonify({'version': table['version'], 'status': table['status'],
                    'turn': (table.get('hand') or {}).get('turn')})

@app.post('/table/<table_id>/start')
def start_table_hand(table_id):
    name = session.get('player_name')
    table = tables.get(table_id)
    if not table or name != table['creator'] or table['status'] == 'active':
        return redirect(url_for('multi_table', table_id=table_id))
    start_multi_hand(table)
    return redirect(url_for('multi_table', table_id=table_id))

@app.post('/table/<table_id>/action')
def multi_action(table_id):
    name = session.get('player_name')
    table = tables.get(table_id)
    hand = table.get('hand') if table else None
    if not hand or table['status'] != 'active' or name != hand.get('turn') or name not in hand['order']:
        return redirect(url_for('multi_table', table_id=table_id))
    move = request.form.get('action', '')
    raw = request.form.get('amount', '').strip()
    try:
        amount = int(raw) if raw else 0
    except ValueError:
        amount = 0
    due = max(0, hand['current_bet'] - hand['committed'][name])
    if move == 'fold':
        hand['folded'].add(name)
        hand['pending'].discard(name)
        hand['message'] = f'{name} folds.'
    elif move == 'check':
        if due:
            hand['message'] = f'{name} must call {due}, raise, or fold.'
            return redirect(url_for('multi_table', table_id=table_id))
        hand['pending'].discard(name)
        hand['message'] = f'{name} double-checks.' if hand['double_check_phase'] and name == hand['opener'] else f'{name} checks.'
    elif move == 'call':
        if due <= 0:
            hand['message'] = 'There is nothing to call.'
            return redirect(url_for('multi_table', table_id=table_id))
        paid = take_multi_chips(hand, name, due)
        hand['pending'].discard(name)
        hand['message'] = f'{name} calls {paid}' + (' and is all-in.' if paid < due or hand['balances'][name] == 0 else '.')
    elif move == 'bet':
        if hand['current_bet'] or amount <= 0 or amount > hand['balances'][name]:
            hand['message'] = 'That bet is not available.'
            return redirect(url_for('multi_table', table_id=table_id))
        paid = take_multi_chips(hand, name, amount)
        hand['current_bet'] = hand['committed'][name]
        hand['pending'] = {p for p in active_multi_players(hand) if p != name and hand['balances'][p] > 0}
        hand['message'] = f'{name} bets {paid}.'
    elif move == 'raise':
        total = due + amount
        if due <= 0 or amount <= 0 or total > hand['balances'][name]:
            hand['message'] = 'That raise is not available.'
            return redirect(url_for('multi_table', table_id=table_id))
        take_multi_chips(hand, name, total)
        hand['current_bet'] = hand['committed'][name]
        hand['pending'] = {p for p in active_multi_players(hand) if p != name and hand['balances'][p] > 0}
        hand['message'] = f'{name} calls {due} and raises {amount}.'
    else:
        return redirect(url_for('multi_table', table_id=table_id))
    advance_multi_after_action(table, hand, name)
    return redirect(url_for('multi_table', table_id=table_id))

@app.post('/table/<table_id>/next')
def next_table_hand(table_id):
    name = session.get('player_name')
    table = tables.get(table_id)
    if table and name == table['creator'] and table['status'] == 'finished':
        start_multi_hand(table)
    return redirect(url_for('multi_table', table_id=table_id))

@app.post('/table/<table_id>/pause')
def toggle_pause(table_id):
    name = session.get('player_name')
    table = tables.get(table_id)
    if table and name in table['players']:
        account = player_record(name)
        account['paused'] = not account['paused']
        bump_table(table)
    return redirect(url_for('multi_table', table_id=table_id))

@app.post('/table/<table_id>/leave')
def leave_table(table_id):
    name = session.get('player_name')
    table = tables.get(table_id)
    if table and name in table['players']:
        hand = table.get('hand')
        if table['status'] == 'active' and hand and name in hand['order'] and name not in hand['folded']:
            was_turn = hand.get('turn') == name
            hand['folded'].add(name)
            hand['pending'].discard(name)
            hand['message'] = f'{name} leaves the table and folds.'
            if was_turn:
                advance_multi_after_action(table, hand, name)
        table['players'].remove(name)
        account = player_record(name)
        account['table_id'] = None
        account['paused'] = False
        if not table['players']:
            table['creator'] = None
            table['status'] = 'waiting'
            table['hand'] = None
            table['first_actor_index'] = 0
        elif table['creator'] == name:
            table['creator'] = table['players'][0]
        if table['status'] != 'active':
            table['hand'] = None
            table['status'] = 'waiting'
        bump_table(table)
    return redirect(url_for('table_lobby', mode=table['mode'] if table else 'multi'))

if __name__ == '__main__':
    print('ONI is running with Play Benny, Head-to-Head, and Multi Table. Open http://127.0.0.1:5005')
    print('For another computer on the same Wi-Fi, use this computer\'s local IP address with :5005')
    app.run(host='0.0.0.0', port=5005, debug=False)
