import streamlit as st
import streamlit.components.v1 as components
st.title("THIS IS MAIN.PY ✅")
st.set_page_config(page_title="K-Arcade Shooter (10sec)", layout="wide")

st.title("🕹️ 10초 생존 오락실 비행기 슈팅 (Streamlit)")
st.caption("방향키: 이동 / Q: 단발 / W: 스프레드 / 10초 생존하면 클리어")

if "seed" not in st.session_state:
    st.session_state.seed = 0

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🔄 재시작"):
        st.session_state.seed += 1
with col2:
    st.write("")

GAME_HTML = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <style>
    body {{ margin:0; background:#0b1020; color:#e8eefc; font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; }}
    .wrap {{ display:flex; flex-direction:column; align-items:center; gap:10px; padding:10px; }}
    canvas {{ background: radial-gradient(ellipse at center, #0f1b3b 0%, #070b18 70%); border:1px solid rgba(255,255,255,0.15); border-radius:12px; }}
    .hud {{ width: 820px; display:flex; justify-content:space-between; align-items:center; }}
    .pill {{ padding:6px 10px; border-radius:999px; background: rgba(255,255,255,0.10); border:1px solid rgba(255,255,255,0.12); font-size:14px; }}
    .help {{ width: 820px; font-size:13px; opacity:0.9; line-height:1.35; }}
    .overlay {{
      position:absolute; inset:0; display:none; align-items:center; justify-content:center;
      background: rgba(0,0,0,0.55); border-radius:12px;
    }}
    .panel {{
      width: 520px; padding:18px 18px; border-radius:16px;
      background: rgba(15, 25, 60, 0.92); border:1px solid rgba(255,255,255,0.18);
      box-shadow: 0 10px 30px rgba(0,0,0,0.35);
      text-align:center;
    }}
    .panel h2 {{ margin: 0 0 10px 0; }}
    .panel p {{ margin: 8px 0; opacity: 0.95; }}
    .btn {{
      margin-top: 12px;
      padding:10px 14px; border-radius:12px; border:1px solid rgba(255,255,255,0.22);
      background: rgba(255,255,255,0.10); color: #e8eefc; cursor:pointer; font-size:14px;
    }}
    .btn:hover {{ background: rgba(255,255,255,0.16); }}
    .stage {{
      position: relative;
      width: 820px;
      height: 520px;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hud">
      <div class="pill" id="timePill">Time: 60.0</div>
      <div class="pill" id="scorePill">Score: 0</div>
      <div class="pill" id="statusPill">Status: PLAY</div>
    </div>

    <div class="stage">
      <canvas id="c" width="820" height="520" tabindex="0"></canvas>
      <div class="overlay" id="overlay">
        <div class="panel">
          <h2 id="resultTitle">RESULT</h2>
          <p id="resultBody">...</p>
          <button class="btn" id="restartBtn">다시하기</button>
          <p style="font-size:12px; opacity:0.85; margin-top:10px;">
            * Streamlit 상단 "재시작" 버튼을 눌러도 됩니다.
          </p>
        </div>
      </div>
    </div>

    <div class="help">
      <b>조작</b>: 방향키 이동 / <b>Q</b> 단발 / <b>W</b> 스프레드<br/>
      <b>규칙</b>: 10초 동안 적 비행기(및 탄)와 충돌하지 않고 살아남으면 클리어.
    </div>
  </div>

<script>
(() => {{
  const SEED = {st.session_state.seed};
  let rngState = (SEED + 1) * 1234567;
  function rand() {{
    rngState = (1103515245 * rngState + 12345) >>> 0;
    return (rngState & 0x7fffffff) / 0x80000000;
  }}

  const canvas = document.getElementById("c");
  const ctx = canvas.getContext("2d");
  canvas.focus();

  const overlay = document.getElementById("overlay");
  const resultTitle = document.getElementById("resultTitle");
  const resultBody = document.getElementById("resultBody");
  const restartBtn = document.getElementById("restartBtn");

  const timePill = document.getElementById("timePill");
  const scorePill = document.getElementById("scorePill");
  const statusPill = document.getElementById("statusPill");

  const W = canvas.width, H = canvas.height;

  // ----- Game constants -----
  const GAME_SECONDS = 10.0;
  const player = {{
    x: W * 0.5, y: H * 0.82,
    r: 12,
    speed: 340, // px/s
    invuln: 0,
  }};

  let bullets = [];   // player bullets
  let ebullets = [];  // enemy bullets
  let enemies = [];
  let stars = [];
  let score = 0;

  let keys = {{}};
  let running = true;
  let tLeft = GAME_SECONDS;
  let last = performance.now();

  for (let i=0;i<120;i++) {{
    stars.push({{
      x: rand()*W, y: rand()*H,
      s: 0.5 + rand()*1.8,
      v: 25 + rand()*80
    }});
  }}

  function clamp(v, a, b) {{ return Math.max(a, Math.min(b, v)); }}

  function reset() {{
    bullets = [];
    ebullets = [];
    enemies = [];
    score = 0;
    running = true;
    tLeft = GAME_SECONDS;
    player.x = W*0.5;
    player.y = H*0.82;
    player.invuln = 0;
    overlay.style.display = "none";
    statusPill.textContent = "Status: PLAY";
    last = performance.now();
  }}

  window.addEventListener("keydown", (e) => {{
    if (["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"," "].includes(e.key)) e.preventDefault();
    keys[e.key.toLowerCase()] = true;
    keys[e.key] = true;

    if (!running && (e.key.toLowerCase() === "r")) reset();
  }}, {{ passive:false }});

  window.addEventListener("keyup", (e) => {{
    keys[e.key.toLowerCase()] = false;
    keys[e.key] = false;
  }});

  restartBtn.addEventListener("click", () => reset());

  let spawnTimer = 0;
  function spawnEnemy() {{
    const kind = rand() < 0.65 ? "fighter" : "zigzag";
    const x = 60 + rand()*(W-120);
    const y = -30;
    const baseSpeed = 110 + rand()*110;

    const e = {{
      kind,
      x, y,
      r: kind === "fighter" ? 16 : 18,
      hp: kind === "fighter" ? 2 : 3,
      vy: baseSpeed,
      vx: (kind === "zigzag" ? (rand()<0.5?-1:1) * (70 + rand()*90) : 0),
      shootCd: 0.6 + rand()*0.9
    }};
    enemies.push(e);
  }}

  function fireQ() {{
    bullets.push({{
      x: player.x, y: player.y-18,
      vx: 0, vy: -520,
      r: 4, dmg: 1
    }});
  }}

  function fireW() {{
    const angles = [-0.25, 0, 0.25];
    for (const a of angles) {{
      bullets.push({{
        x: player.x, y: player.y-18,
        vx: Math.sin(a)*240,
        vy: -520*Math.cos(a),
        r: 4, dmg: 1
      }});
    }}
  }}

  let fireLockQ = 0;
  let fireLockW = 0;

  function enemyShoot(e) {{
    const dx = player.x - e.x;
    const dy = (player.y) - (e.y);
    const len = Math.max(1, Math.hypot(dx, dy));
    const spd = 220 + rand()*90;
    ebullets.push({{
      x: e.x, y: e.y + 14,
      vx: (dx/len)*spd,
      vy: (dy/len)*spd,
      r: 4
    }});
  }}

  function circleHit(ax, ay, ar, bx, by, br) {{
    const dx = ax - bx, dy = ay - by;
    return (dx*dx + dy*dy) <= (ar+br)*(ar+br);
  }}

  function endGame(win) {{
    running = false;
    statusPill.textContent = "Status: END";
    overlay.style.display = "flex";
    resultTitle.textContent = win ? "🎉 CLEAR!" : "💥 GAME OVER";
    resultBody.textContent = win
      ? `10초 생존 성공! 점수: ${{score}}`
      : `충돌했습니다. 점수: ${{score}}`;
  }}

  function update(dt) {{
    if (!running) return;

    tLeft -= dt;
    if (tLeft <= 0) {{
      tLeft = 0;
      endGame(true);
      return;
    }}

    let mx = 0, my = 0;
    if (keys["arrowleft"]) mx -= 1;
    if (keys["arrowright"]) mx += 1;
    if (keys["arrowup"]) my -= 1;
    if (keys["arrowdown"]) my += 1;

    const norm = Math.hypot(mx,my) || 1;
    mx /= norm; my /= norm;

    player.x = clamp(player.x + mx * player.speed * dt, 20, W-20);
    player.y = clamp(player.y + my * player.speed * dt, 30, H-20);

    fireLockQ -= dt;
    fireLockW -= dt;
    if (keys["q"] && fireLockQ <= 0) {{
      fireQ();
      fireLockQ = 0.13; // rate limit
    }}
    if (keys["w"] && fireLockW <= 0) {{
      fireW();
      fireLockW = 0.35;
    }}

    for (const s of stars) {{
      s.y += s.v * dt;
      if (s.y > H) {{ s.y = -5; s.x = rand()*W; }}
    }}

    spawnTimer -= dt;
    const ramp = 1 - (tLeft / GAME_SECONDS); // 0 -> 1
    const spawnEvery = 0.55 - 0.25*ramp;     // faster over time
    if (spawnTimer <= 0) {{
      spawnEnemy();
      if (rand() < 0.20 + 0.25*ramp) spawnEnemy(); // sometimes double spawn later
      spawnTimer = spawnEvery;
    }}

    for (const e of enemies) {{
      e.y += e.vy * dt;
      e.x += e.vx * dt;
      if (e.kind === "zigzag") {{
        if (e.x < 40 || e.x > W-40) e.vx *= -1;
      }}
      e.shootCd -= dt;
      if (e.shootCd <= 0) {{
        enemyShoot(e);
        e.shootCd = 0.7 + rand()*1.1 - 0.35*ramp;
        e.shootCd = Math.max(0.25, e.shootCd);
      }}
    }}
    enemies = enemies.filter(e => e.y < H + 60 && e.hp > 0);

    for (const b of bullets) {{
      b.x += b.vx * dt;
      b.y += b.vy * dt;
    }}
    bullets = bullets.filter(b => b.y > -40 && b.x > -40 && b.x < W+40);

    for (const b of ebullets) {{
      b.x += b.vx * dt;
      b.y += b.vy * dt;
    }}
    ebullets = ebullets.filter(b => b.y > -60 && b.y < H+60 && b.x > -60 && b.x < W+60);

    for (const b of bullets) {{
      for (const e of enemies) {{
        if (circleHit(b.x,b.y,b.r, e.x,e.y,e.r)) {{
          e.hp -= b.dmg;
          b.y = -9999; 
          if (e.hp <= 0) {{
            score += (e.kind === "fighter" ? 120 : 180);
          }}
          break;
        }}
      }}
    }}
    bullets = bullets.filter(b => b.y > -1000);

    for (const e of enemies) {{
      if (circleHit(player.x,player.y,player.r, e.x,e.y,e.r)) {{
        endGame(false);
        return;
      }}
    }}
    for (const b of ebullets) {{
      if (circleHit(player.x,player.y,player.r, b.x,b.y,b.r)) {{
        endGame(false);
        return;
      }}
    }}

    score += Math.floor(8 * dt);
  }}

  function draw() {{
    ctx.clearRect(0,0,W,H);

    ctx.globalAlpha = 0.85;
    for (const s of stars) {{
      ctx.fillStyle = "rgba(255,255,255,0.85)";
      ctx.fillRect(s.x, s.y, s.s, s.s);
    }}
    ctx.globalAlpha = 1;

    for (const b of bullets) {{
      ctx.beginPath();
      ctx.fillStyle = "rgba(120, 220, 255, 0.95)";
      ctx.arc(b.x, b.y, b.r, 0, Math.PI*2);
      ctx.fill();
    }}

    for (const b of ebullets) {{
      ctx.beginPath();
      ctx.fillStyle = "rgba(255, 170, 90, 0.95)";
      ctx.arc(b.x, b.y, b.r, 0, Math.PI*2);
      ctx.fill();
    }}

    for (const e of enemies) {{
      ctx.save();
      ctx.translate(e.x, e.y);
      ctx.fillStyle = (e.kind === "fighter") ? "rgba(255, 90, 120, 0.92)" : "rgba(255, 130, 60, 0.92)";
      ctx.strokeStyle = "rgba(255,255,255,0.25)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(0, -18);
      ctx.lineTo(14, 14);
      ctx.lineTo(0, 8);
      ctx.lineTo(-14, 14);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();

      // HP bar
      const hpMax = (e.kind === "fighter") ? 2 : 3;
      ctx.fillStyle = "rgba(255,255,255,0.25)";
      ctx.fillRect(-16, -26, 32, 4);
      ctx.fillStyle = "rgba(110, 255, 160, 0.85)";
      ctx.fillRect(-16, -26, 32*(e.hp/hpMax), 4);

      ctx.restore();
    }}

    // player
    ctx.save();
    ctx.translate(player.x, player.y);
    ctx.fillStyle = "rgba(110, 255, 160, 0.95)";
    ctx.strokeStyle = "rgba(255,255,255,0.25)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, -20);
    ctx.lineTo(16, 16);
    ctx.lineTo(0, 10);
    ctx.lineTo(-16, 16);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "rgba(0,0,0,0.25)";
    ctx.beginPath();
    ctx.arc(0, -4, 6, 0, Math.PI*2);
    ctx.fill();
    ctx.restore();

    timePill.textContent = "Time: " + tLeft.toFixed(1);
    scorePill.textContent = "Score: " + score;
  }}

  function loop(now) {{
    const dt = Math.min(0.033, (now - last) / 1000);
    last = now;
    update(dt);
    draw();
    requestAnimationFrame(loop);
  }}

  reset();
  requestAnimationFrame(loop);
}})();
</script>
</body>
</html>
"""

components.html(GAME_HTML, height=640, scrolling=False)

st.markdown(
    """
```bash
pip install streamlit
streamlit run main.py
"""
)