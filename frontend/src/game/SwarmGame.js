// ============================================================
// SWARM MIND — A Swarm Intelligence Survival Game
// "Vampire Survivors meets Boids" — your swarm IS the weapon
// ============================================================

// --- CONFIG ---
const C = {
  BG: '#06060f',
  GRID_COLOR: 'rgba(255,255,255,0.025)',
  GRID_SIZE: 50,

  PLAYER_RADIUS: 14,
  PLAYER_COLOR: '#00e5ff',
  PLAYER_HP: 100,
  PLAYER_MAGNET: 130,
  PLAYER_INVULN: 1200,
  PULSE_CD: 3000,
  PULSE_R: 160,
  PULSE_DMG: 25,

  INIT_AGENTS: 8,
  MAX_AGENTS: 200,
  AGENT_R: 4.5,
  AGENT_SPD: 3.5,
  AGENT_DMG: 8,
  AGENT_HP: 25,
  AGENT_ATK_RANGE: 90,
  AGENT_ATK_CD: 700,

  BOID_SEP: 22, BOID_ALI: 50, BOID_COH: 80,
  BOID_SEP_W: 2.2, BOID_ALI_W: 0.4, BOID_COH_W: 0.7, BOID_FOLLOW_W: 1.6,
  BOID_MAX_SPD: 4.2,

  MAX_PARTICLES: 600,
  WAVE_BREAK: 4000,
  BASE_ENEMIES: 5,
  ENEMY_SCALE: 3,
  BOSS_EVERY: 5,
  XP_MAGNET_SPD: 9,
};

// --- UTILS ---
const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
const norm = (x, y) => { const l = Math.hypot(x, y); return l ? { x: x / l, y: y / l } : { x: 0, y: 0 }; };
const lerp = (a, b, t) => a + (b - a) * t;
const rand = (lo, hi) => Math.random() * (hi - lo) + lo;
const randInt = (lo, hi) => Math.floor(rand(lo, hi + 1));
const pick = arr => arr[Math.floor(Math.random() * arr.length)];
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

// --- AUDIO ENGINE (procedural synth) ---
class Audio {
  constructor() { this.ctx = null; this.gain = null; this.on = true; }

  init() {
    try {
      this.ctx = new (window.AudioContext || window.webkitAudioContext)();
      this.gain = this.ctx.createGain();
      this.gain.gain.value = 0.25;
      this.gain.connect(this.ctx.destination);
    } catch { this.on = false; }
  }

  _osc(freq, type, dur, vol = 0.2, ramp = null) {
    if (!this.on || !this.ctx) return;
    if (this.ctx.state === 'suspended') this.ctx.resume();
    const o = this.ctx.createOscillator();
    const g = this.ctx.createGain();
    o.connect(g); g.connect(this.gain);
    const t = this.ctx.currentTime;
    o.type = type;
    o.frequency.setValueAtTime(freq, t);
    if (ramp) o.frequency.exponentialRampToValueAtTime(ramp, t + dur * 0.8);
    g.gain.setValueAtTime(vol, t);
    g.gain.exponentialRampToValueAtTime(0.001, t + dur);
    o.start(t); o.stop(t + dur);
  }

  kill()    { this._osc(440, 'square', 0.12, 0.15, 880); }
  pickup()  { this._osc(700, 'sine', 0.08, 0.12, 1400); }
  hit()     { this._osc(150, 'sawtooth', 0.18, 0.25, 50); }
  pulse()   { this._osc(220, 'sine', 0.25, 0.2, 80); }
  wave()    { this._osc(350, 'triangle', 0.35, 0.18, 700); }

  levelup() {
    if (!this.on || !this.ctx) return;
    if (this.ctx.state === 'suspended') this.ctx.resume();
    [523, 659, 784, 1047].forEach((f, i) => {
      const o = this.ctx.createOscillator(), g = this.ctx.createGain();
      o.connect(g); g.connect(this.gain);
      const t = this.ctx.currentTime + i * 0.07;
      o.type = 'sine'; o.frequency.setValueAtTime(f, t);
      g.gain.setValueAtTime(0.12, t);
      g.gain.exponentialRampToValueAtTime(0.001, t + 0.18);
      o.start(t); o.stop(t + 0.18);
    });
  }

  gameover() {
    if (!this.on || !this.ctx) return;
    [400, 340, 280, 180].forEach((f, i) => {
      const o = this.ctx.createOscillator(), g = this.ctx.createGain();
      o.connect(g); g.connect(this.gain);
      const t = this.ctx.currentTime + i * 0.14;
      o.type = 'triangle'; o.frequency.setValueAtTime(f, t);
      g.gain.setValueAtTime(0.18, t);
      g.gain.exponentialRampToValueAtTime(0.001, t + 0.28);
      o.start(t); o.stop(t + 0.28);
    });
  }

  toggle() { this.on = !this.on; return this.on; }
}

// --- UPGRADE POOL ---
const UPGRADES = [
  { id: 'agents5',    name: '+5 Agents',       desc: 'Recruit 5 more swarm agents',          icon: '\u{1F41F}', apply: g => { for (let i = 0; i < 5; i++) g.spawnAgent(); } },
  { id: 'agents10',   name: '+10 Agents',      desc: 'Mass recruit 10 agents',               icon: '\u{1F300}', apply: g => { for (let i = 0; i < 10; i++) g.spawnAgent(); } },
  { id: 'agentSpd',   name: 'Swift Swarm',     desc: 'Agents move 20% faster',               icon: '\u{1F4A8}', apply: g => { g.mult.agentSpd *= 1.2; } },
  { id: 'agentDmg',   name: 'Sharp Fangs',     desc: 'Agents deal 25% more damage',          icon: '\u2694\uFE0F',  apply: g => { g.mult.agentDmg *= 1.25; } },
  { id: 'agentHp',    name: 'Thick Scales',    desc: 'Agents gain 30% more HP',              icon: '\u{1F6E1}\uFE0F',  apply: g => { g.mult.agentHp *= 1.3; g.agents.forEach(a => { a.maxHp *= 1.3; a.hp = a.maxHp; }); } },
  { id: 'magnet',     name: 'Magnetic Pull',   desc: 'Pickup range +50%',                    icon: '\u{1F9F2}', apply: g => { g.mult.magnet *= 1.5; } },
  { id: 'pulseDmg',   name: 'Shockwave+',      desc: 'Pulse deals 40% more damage',          icon: '\u{1F4A5}', apply: g => { g.mult.pulseDmg *= 1.4; } },
  { id: 'pulseR',     name: 'Wide Pulse',      desc: 'Pulse radius +35%',                    icon: '\u{1F30A}', apply: g => { g.mult.pulseR *= 1.35; } },
  { id: 'pulseCd',    name: 'Rapid Pulse',     desc: 'Pulse cooldown -25%',                  icon: '\u26A1',    apply: g => { g.mult.pulseCd *= 0.75; } },
  { id: 'hp',         name: 'Vital Core',      desc: 'Max HP +30, heal to full',             icon: '\u2764\uFE0F',  apply: g => { g.player.maxHp += 30; g.player.hp = g.player.maxHp; } },
  { id: 'regen',      name: 'Regeneration',    desc: 'Slowly regenerate HP',                 icon: '\u{1F49A}', apply: g => { g.mult.regen += 0.8; } },
  { id: 'xp',         name: 'Quick Learner',   desc: 'XP from kills +30%',                   icon: '\u{1F4C8}', apply: g => { g.mult.xp *= 1.3; } },
  { id: 'atkSpd',     name: 'Frenzy',          desc: 'Agents attack 20% faster',             icon: '\u{1F525}', apply: g => { g.mult.atkSpd *= 0.8; } },
  { id: 'spread',     name: 'Wide Formation',  desc: 'Agents spread out for better coverage',icon: '\u{1F310}', apply: g => { g.mult.boidSep += 0.5; } },
];

// --- ENEMY DEFS ---
const ENEMIES = {
  drone:    { r: 8,  hp: 30,  spd: 1.5, dmg: 10, color: '#ff1744', xp: 10, pts: 10 },
  fast:     { r: 6,  hp: 15,  spd: 3.2, dmg: 7,  color: '#ff9100', xp: 8,  pts: 15 },
  tank:     { r: 16, hp: 120, spd: 0.7, dmg: 20, color: '#d500f9', xp: 30, pts: 25 },
  splitter: { r: 12, hp: 45,  spd: 1.2, dmg: 12, color: '#ffea00', xp: 15, pts: 20 },
  boss:     { r: 32, hp: 500, spd: 0.5, dmg: 35, color: '#ff1744', xp: 100,pts: 200 },
};

// ============================================================
// MAIN GAME CLASS
// ============================================================
export default class SwarmGame {
  constructor(canvas, emit) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.emit = emit || (() => {});

    // dimensions
    this.w = 0; this.h = 0;

    // state
    this.state = 'menu'; // menu | playing | upgrade | gameover
    this.score = 0;
    this.wave = 0;
    this.kills = 0;
    this.combo = 0;
    this.comboTimer = 0;
    this.xp = 0;
    this.xpNeed = 100;
    this.level = 1;
    this.time = 0;
    this.highScore = parseInt(localStorage.getItem('swarm_hs') || '0', 10);

    // camera
    this.cam = { x: 0, y: 0 };
    this.shake = { x: 0, y: 0, pow: 0 };

    // player
    this.player = { x: 0, y: 0, tx: 0, ty: 0, r: C.PLAYER_RADIUS, hp: C.PLAYER_HP, maxHp: C.PLAYER_HP, invuln: 0, pulseCd: 0 };

    // entities
    this.agents = [];
    this.enemies = [];
    this.particles = [];
    this.pickups = [];
    this.dmgNums = [];
    this.pulses = [];

    // multipliers
    this.mult = { agentSpd: 1, agentDmg: 1, agentHp: 1, magnet: 1, pulseDmg: 1, pulseR: 1, pulseCd: 1, regen: 0, xp: 1, atkSpd: 1, boidSep: 0 };

    // wave state
    this.waveActive = false;
    this.waveEnemiesLeft = 0;
    this.waveSpawnCd = 0;
    this.wavePause = 0;
    this.pendingUpgrade = false;
    this.upgradeChoices = [];

    // input
    this.mouse = { x: 0, y: 0 };

    // menu decorations
    this.menuSwarm = [];

    // audio
    this.audio = new Audio();

    // loop
    this.running = false;
    this.lastT = 0;
    this.raf = null;

    // bind
    this._loop = this._loop.bind(this);
    this._onMM = this._onMM.bind(this);
    this._onMD = this._onMD.bind(this);
    this._onResize = this._onResize.bind(this);
    this._onKey = this._onKey.bind(this);
  }

  // --- LIFECYCLE ---
  init() {
    this._onResize();
    window.addEventListener('resize', this._onResize);
    this.canvas.addEventListener('mousemove', this._onMM);
    this.canvas.addEventListener('mousedown', this._onMD);
    this.canvas.addEventListener('contextmenu', e => e.preventDefault());
    window.addEventListener('keydown', this._onKey);

    // Touch support
    this.canvas.addEventListener('touchstart', e => { e.preventDefault(); this._touchToMouse(e); this._onMD(e); }, { passive: false });
    this.canvas.addEventListener('touchmove', e => { e.preventDefault(); this._touchToMouse(e); }, { passive: false });

    this._initMenu();
    this.running = true;
    this.lastT = performance.now();
    this._loop();
  }

  destroy() {
    this.running = false;
    if (this.raf) cancelAnimationFrame(this.raf);
    window.removeEventListener('resize', this._onResize);
    this.canvas.removeEventListener('mousemove', this._onMM);
    this.canvas.removeEventListener('mousedown', this._onMD);
    window.removeEventListener('keydown', this._onKey);
  }

  _touchToMouse(e) {
    const t = e.touches[0];
    if (!t) return;
    const r = this.canvas.getBoundingClientRect();
    this.mouse.x = t.clientX - r.left;
    this.mouse.y = t.clientY - r.top;
    if (this.state === 'playing') {
      this.player.tx = this.mouse.x + this.cam.x;
      this.player.ty = this.mouse.y + this.cam.y;
    }
  }

  _onResize() {
    const p = this.canvas.parentElement;
    this.canvas.width = p ? p.clientWidth : window.innerWidth;
    this.canvas.height = p ? p.clientHeight : window.innerHeight;
    this.w = this.canvas.width;
    this.h = this.canvas.height;
  }

  _onMM(e) {
    const r = this.canvas.getBoundingClientRect();
    this.mouse.x = e.clientX - r.left;
    this.mouse.y = e.clientY - r.top;
    if (this.state === 'playing') {
      this.player.tx = this.mouse.x + this.cam.x;
      this.player.ty = this.mouse.y + this.cam.y;
    }
  }

  _onMD() {
    if (this.state === 'menu') { this.audio.init(); this._startGame(); }
    else if (this.state === 'playing') this._pulse();
    else if (this.state === 'gameover') this._startGame();
  }

  _onKey(e) {
    if (this.state === 'upgrade') {
      const n = parseInt(e.key);
      if (n >= 1 && n <= 3) this.selectUpgrade(n - 1);
    }
    if (e.key === 'm' || e.key === 'M') {
      const on = this.audio.toggle();
      this.emit('sound', on);
    }
    if (e.key === ' ' && this.state === 'playing') {
      e.preventDefault();
      this._pulse();
    }
  }

  // --- MENU ---
  _initMenu() {
    this.menuSwarm = [];
    for (let i = 0; i < 100; i++) {
      this.menuSwarm.push({
        x: Math.random() * (this.w || 900),
        y: Math.random() * (this.h || 600),
        vx: rand(-1, 1), vy: rand(-1, 1),
        r: rand(2.5, 6), hue: rand(170, 210),
      });
    }
  }

  _updateMenu(dt) {
    const cx = this.mouse.x || this.w / 2;
    const cy = this.mouse.y || this.h / 2;
    for (const a of this.menuSwarm) {
      const dx = cx - a.x, dy = cy - a.y;
      const d = Math.hypot(dx, dy);
      if (d > 20) { a.vx += (dx / d) * 0.04; a.vy += (dy / d) * 0.04; }
      for (const b of this.menuSwarm) {
        if (a === b) continue;
        const bx = a.x - b.x, by = a.y - b.y;
        const bd = Math.hypot(bx, by);
        if (bd < 28 && bd > 0) { a.vx += (bx / bd) * 0.25; a.vy += (by / bd) * 0.25; }
      }
      const s = Math.hypot(a.vx, a.vy);
      if (s > 2.5) { a.vx = (a.vx / s) * 2.5; a.vy = (a.vy / s) * 2.5; }
      a.x += a.vx; a.y += a.vy;
      if (a.x < -20) a.x = this.w + 20;
      if (a.x > this.w + 20) a.x = -20;
      if (a.y < -20) a.y = this.h + 20;
      if (a.y > this.h + 20) a.y = -20;
    }
  }

  // --- GAME START ---
  _startGame() {
    this.score = 0; this.wave = 0; this.kills = 0;
    this.combo = 0; this.comboTimer = 0;
    this.xp = 0; this.xpNeed = 100; this.level = 1; this.time = 0;

    Object.assign(this.player, { x: 0, y: 0, tx: 0, ty: 0, hp: C.PLAYER_HP, maxHp: C.PLAYER_HP, invuln: 0, pulseCd: 0 });
    this.agents = []; this.enemies = []; this.particles = []; this.pickups = []; this.dmgNums = []; this.pulses = [];
    this.mult = { agentSpd: 1, agentDmg: 1, agentHp: 1, magnet: 1, pulseDmg: 1, pulseR: 1, pulseCd: 1, regen: 0, xp: 1, atkSpd: 1, boidSep: 0 };
    this.waveActive = false; this.wavePause = 2500; this.pendingUpgrade = false;

    this.cam = { x: -this.w / 2, y: -this.h / 2 };
    for (let i = 0; i < C.INIT_AGENTS; i++) this.spawnAgent();
    this.state = 'playing';
    this.emit('state', { state: 'playing' });
  }

  // --- SPAWNING ---
  spawnAgent() {
    if (this.agents.length >= C.MAX_AGENTS) return;
    const a = Math.random() * Math.PI * 2;
    const d = rand(30, 60);
    this.agents.push({
      x: this.player.x + Math.cos(a) * d,
      y: this.player.y + Math.sin(a) * d,
      vx: 0, vy: 0,
      r: C.AGENT_R,
      hp: C.AGENT_HP * this.mult.agentHp,
      maxHp: C.AGENT_HP * this.mult.agentHp,
      dmg: C.AGENT_DMG * this.mult.agentDmg,
      atkCd: 0,
      hue: rand(170, 200),
      trail: [],
    });
  }

  spawnEnemy(type, x, y) {
    const def = ENEMIES[type]; if (!def) return;
    if (x === undefined) {
      const side = randInt(0, 3), m = 120;
      if (side === 0)      { x = this.player.x + rand(-this.w, this.w); y = this.player.y - this.h / 2 - m; }
      else if (side === 1) { x = this.player.x + this.w / 2 + m; y = this.player.y + rand(-this.h, this.h); }
      else if (side === 2) { x = this.player.x + rand(-this.w, this.w); y = this.player.y + this.h / 2 + m; }
      else                 { x = this.player.x - this.w / 2 - m; y = this.player.y + rand(-this.h, this.h); }
    }
    const sc = 1 + (this.wave - 1) * 0.1;
    this.enemies.push({
      x, y, vx: 0, vy: 0, type,
      r: def.r, hp: def.hp * sc, maxHp: def.hp * sc, spd: def.spd,
      dmg: def.dmg * sc, color: def.color, xp: def.xp, pts: def.pts,
      flash: 0, dead: false,
    });
  }

  _spawnParticles(x, y, color, n = 5, spd = 3, life = 500) {
    for (let i = 0; i < n; i++) {
      if (this.particles.length >= C.MAX_PARTICLES) this.particles.shift();
      const a = Math.random() * Math.PI * 2;
      const s = rand(0.5, spd);
      this.particles.push({ x, y, vx: Math.cos(a) * s, vy: Math.sin(a) * s, life: rand(life * 0.5, life), maxLife: life, r: rand(1.5, 3.5), color });
    }
  }

  _spawnDmg(x, y, val, color = '#fff') {
    this.dmgNums.push({ x, y, val: Math.round(val), color, life: 700, maxLife: 700, vy: -2.5 });
  }

  // --- PULSE ATTACK ---
  _pulse() {
    if (this.player.pulseCd > 0) return;
    const cd = C.PULSE_CD * this.mult.pulseCd;
    this.player.pulseCd = cd;
    this.audio.pulse();
    const pr = C.PULSE_R * this.mult.pulseR;
    this.pulses.push({ x: this.player.x, y: this.player.y, r: 0, maxR: pr, life: 280, maxLife: 280 });
    this.shake.pow = 8;
    const dmg = C.PULSE_DMG * this.mult.pulseDmg;
    for (const e of this.enemies) {
      if (e.dead) continue;
      const d = dist(this.player, e);
      if (d < pr + e.r) {
        this._hurtEnemy(e, dmg);
        const n = norm(e.x - this.player.x, e.y - this.player.y);
        e.vx += n.x * 12; e.vy += n.y * 12;
      }
    }
  }

  // --- DAMAGE ---
  _hurtEnemy(e, dmg) {
    e.hp -= dmg; e.flash = 80;
    this._spawnDmg(e.x, e.y - e.r, dmg, '#ffeb3b');
    this._spawnParticles(e.x, e.y, e.color, 3, 2, 250);
    if (e.hp <= 0) this._killEnemy(e);
  }

  _killEnemy(e) {
    e.dead = true;
    this.kills++;
    this.waveEnemiesLeft = Math.max(0, this.waveEnemiesLeft - 1);
    this.combo++; this.comboTimer = 2000;
    const cm = Math.min(1 + this.combo * 0.1, 5);
    this.score += Math.round(e.pts * cm);

    // drops
    this.pickups.push({ x: e.x + rand(-8, 8), y: e.y + rand(-8, 8), type: 'xp', val: Math.round(e.xp * this.mult.xp), r: 5, mag: false, hue: 50, life: 12000 });
    if (Math.random() < 0.12) {
      this.pickups.push({ x: e.x + rand(-12, 12), y: e.y + rand(-12, 12), type: 'hp', val: 10, r: 6, mag: false, hue: 140, life: 12000 });
    }

    this._spawnParticles(e.x, e.y, e.color, 10, 4, 450);
    this.audio.kill();
    this.shake.pow = Math.max(this.shake.pow, 3);

    if (e.type === 'splitter') {
      for (let i = 0; i < 3; i++) { this.spawnEnemy('fast', e.x + rand(-20, 20), e.y + rand(-20, 20)); this.waveEnemiesLeft++; }
    }
    if (e.type === 'boss') {
      this.shake.pow = 20;
      this._spawnParticles(e.x, e.y, '#fff', 25, 6, 700);
      this._spawnParticles(e.x, e.y, e.color, 18, 5, 600);
      this.score += 500;
    }
  }

  _hurtPlayer(dmg) {
    if (this.player.invuln > 0) return;
    this.player.hp -= dmg;
    this.player.invuln = C.PLAYER_INVULN;
    this.shake.pow = 10;
    this.audio.hit();
    this._spawnParticles(this.player.x, this.player.y, '#ff0000', 8, 3, 350);
    this._spawnDmg(this.player.x, this.player.y - 20, dmg, '#ff5252');
    if (this.player.hp <= 0) { this.player.hp = 0; this._die(); }
  }

  _die() {
    this.state = 'gameover';
    this.audio.gameover();
    this._spawnParticles(this.player.x, this.player.y, '#00e5ff', 35, 6, 900);
    if (this.score > this.highScore) {
      this.highScore = this.score;
      localStorage.setItem('swarm_hs', String(this.score));
    }
    this.emit('state', { state: 'gameover', score: this.score, wave: this.wave, kills: this.kills, time: this.time, hs: this.highScore });
  }

  // --- UPGRADES ---
  _triggerUpgrade() {
    const pool = [...UPGRADES].sort(() => Math.random() - 0.5);
    this.upgradeChoices = pool.slice(0, 3);
    this.state = 'upgrade';
    this.audio.levelup();
    this.emit('state', { state: 'upgrade', choices: this.upgradeChoices, wave: this.wave });
  }

  selectUpgrade(i) {
    if (this.state !== 'upgrade' || i < 0 || i >= this.upgradeChoices.length) return;
    this.upgradeChoices[i].apply(this);
    this.state = 'playing';
    this.pendingUpgrade = false;
    this.wavePause = 2500;
    this.emit('state', { state: 'playing', wave: this.wave });
  }

  // --- XP ---
  _addXp(amt) {
    this.xp += amt;
    while (this.xp >= this.xpNeed) {
      this.xp -= this.xpNeed;
      this.level++;
      this.xpNeed = Math.round(this.xpNeed * 1.25);
      for (let i = 0; i < 2; i++) this.spawnAgent();
      this.audio.levelup();
      this._spawnParticles(this.player.x, this.player.y, '#00e5ff', 12, 4, 500);
    }
  }

  // --- BOIDS ---
  _updateBoids(dt) {
    const dtS = dt / 1000;
    const sepW = C.BOID_SEP_W + this.mult.boidSep;
    for (const ag of this.agents) {
      let sx = 0, sy = 0, ax = 0, ay = 0, ac = 0, cx = 0, cy = 0, cc = 0;
      for (const o of this.agents) {
        if (ag === o) continue;
        const dx = ag.x - o.x, dy = ag.y - o.y;
        const d = Math.hypot(dx, dy);
        if (d < C.BOID_SEP && d > 0) { sx += (dx / d) * (C.BOID_SEP - d); sy += (dy / d) * (C.BOID_SEP - d); }
        if (d < C.BOID_ALI) { ax += o.vx; ay += o.vy; ac++; }
        if (d < C.BOID_COH) { cx += o.x; cy += o.y; cc++; }
      }

      let fx = sx * sepW, fy = sy * sepW;
      if (ac) { fx += ((ax / ac) - ag.vx) * C.BOID_ALI_W; fy += ((ay / ac) - ag.vy) * C.BOID_ALI_W; }
      if (cc) { fx += (cx / cc - ag.x) * 0.01 * C.BOID_COH_W; fy += (cy / cc - ag.y) * 0.01 * C.BOID_COH_W; }

      // follow player
      const px = this.player.x - ag.x, py = this.player.y - ag.y;
      const pd = Math.hypot(px, py);
      if (pd > 220) { fx += (px / pd) * 5; fy += (py / pd) * 5; }
      else if (pd > 35) { fx += (px / pd) * C.BOID_FOLLOW_W; fy += (py / pd) * C.BOID_FOLLOW_W; }

      // attack
      let ne = null, nd = C.AGENT_ATK_RANGE;
      for (const e of this.enemies) { if (e.dead) continue; const d = dist(ag, e); if (d < nd) { nd = d; ne = e; } }
      if (ne) {
        const dx = ne.x - ag.x, dy = ne.y - ag.y, d = Math.hypot(dx, dy);
        if (d > 0) { fx += (dx / d) * 3.5; fy += (dy / d) * 3.5; }
        if (d < ag.r + ne.r + 8 && ag.atkCd <= 0) {
          this._hurtEnemy(ne, ag.dmg);
          ag.atkCd = C.AGENT_ATK_CD * this.mult.atkSpd;
          this._spawnParticles((ag.x + ne.x) / 2, (ag.y + ne.y) / 2, `hsl(${ag.hue},100%,70%)`, 2, 1.5, 150);
        }
      }

      const ms = C.BOID_MAX_SPD * this.mult.agentSpd;
      ag.vx += fx * dtS * 60; ag.vy += fy * dtS * 60;
      const sp = Math.hypot(ag.vx, ag.vy);
      if (sp > ms) { ag.vx = (ag.vx / sp) * ms; ag.vy = (ag.vy / sp) * ms; }
      ag.vx *= 0.98; ag.vy *= 0.98;
      ag.x += ag.vx; ag.y += ag.vy;
      ag.atkCd -= dt;
      ag.trail.push({ x: ag.x, y: ag.y });
      if (ag.trail.length > 6) ag.trail.shift();
    }

    // remove dead agents
    this.agents = this.agents.filter(a => a.hp > 0);
  }

  // --- ENEMIES ---
  _updateEnemies(dt) {
    for (const e of this.enemies) {
      if (e.dead) continue;
      const dx = this.player.x - e.x, dy = this.player.y - e.y, d = Math.hypot(dx, dy);
      if (d > 0) {
        e.vx = lerp(e.vx, (dx / d) * e.spd, 0.05);
        e.vy = lerp(e.vy, (dy / d) * e.spd, 0.05);
      }
      e.x += e.vx; e.y += e.vy;
      e.flash = Math.max(0, e.flash - dt);

      // hit player
      if (dist(e, this.player) < e.r + this.player.r) {
        this._hurtPlayer(e.dmg);
        const n = norm(e.x - this.player.x, e.y - this.player.y);
        e.vx = n.x * 6; e.vy = n.y * 6;
      }

      // damage nearby agents
      for (const ag of this.agents) {
        if (dist(e, ag) < e.r + ag.r + 2) {
          ag.hp -= e.dmg * 0.15 * (dt / 1000);
          if (ag.hp <= 0) {
            this._spawnParticles(ag.x, ag.y, `hsl(${ag.hue},100%,60%)`, 6, 3, 300);
          }
        }
      }
    }
    this.enemies = this.enemies.filter(e => !e.dead);
  }

  // --- WAVES ---
  _updateWaves(dt) {
    if (this.pendingUpgrade) return;
    if (!this.waveActive) {
      this.wavePause -= dt;
      if (this.wavePause <= 0) this._startWave();
      return;
    }
    if (this.waveSpawnCd > 0) this.waveSpawnCd -= dt;
    else if (this.waveEnemiesLeft > 0 && this.enemies.length < 60) {
      const r = Math.random();
      let type = 'drone';
      if (this.wave >= 3 && r < 0.2) type = 'fast';
      if (this.wave >= 5 && r < 0.1) type = 'tank';
      if (this.wave >= 4 && r > 0.85) type = 'splitter';
      if (this.wave % C.BOSS_EVERY === 0 && !this.enemies.some(e => e.type === 'boss')) type = 'boss';
      this.spawnEnemy(type);
      this.waveSpawnCd = Math.max(150, 700 - this.wave * 25);
    }
    if (this.waveEnemiesLeft <= 0 && this.enemies.length === 0) {
      this.waveActive = false;
      this.pendingUpgrade = true;
      this._triggerUpgrade();
    }
  }

  _startWave() {
    this.wave++;
    this.waveActive = true;
    this.waveEnemiesLeft = C.BASE_ENEMIES + (this.wave - 1) * C.ENEMY_SCALE;
    this.waveSpawnCd = 0;
    this.audio.wave();
    this.emit('state', { state: 'wave', wave: this.wave, count: this.waveEnemiesLeft });
  }

  // --- PICKUPS ---
  _updatePickups(dt) {
    const mr = C.PLAYER_MAGNET * this.mult.magnet;
    for (const p of this.pickups) {
      p.life -= dt;
      const d = dist(p, this.player);
      if (d < mr) p.mag = true;
      if (p.mag) {
        const dx = this.player.x - p.x, dy = this.player.y - p.y, dd = Math.hypot(dx, dy);
        if (dd > 0) { p.x += (dx / dd) * C.XP_MAGNET_SPD; p.y += (dy / dd) * C.XP_MAGNET_SPD; }
      }
      if (d < this.player.r + p.r) {
        p.gone = true;
        this.audio.pickup();
        if (p.type === 'xp') this._addXp(p.val);
        else { this.player.hp = Math.min(this.player.hp + p.val, this.player.maxHp); this._spawnParticles(this.player.x, this.player.y, '#69f0ae', 4, 2, 250); }
      }
    }
    this.pickups = this.pickups.filter(p => !p.gone && p.life > 0);
  }

  // --- FX ---
  _updateFx(dt) {
    for (const p of this.particles) { p.x += p.vx; p.y += p.vy; p.vx *= 0.95; p.vy *= 0.95; p.life -= dt; }
    this.particles = this.particles.filter(p => p.life > 0);
    for (const d of this.dmgNums) { d.y += d.vy; d.life -= dt; }
    this.dmgNums = this.dmgNums.filter(d => d.life > 0);
    for (const p of this.pulses) { p.life -= dt; p.r = p.maxR * (1 - p.life / p.maxLife); }
    this.pulses = this.pulses.filter(p => p.life > 0);
    if (this.shake.pow > 0) {
      this.shake.x = (Math.random() - 0.5) * this.shake.pow;
      this.shake.y = (Math.random() - 0.5) * this.shake.pow;
      this.shake.pow *= 0.88;
      if (this.shake.pow < 0.4) this.shake.pow = 0;
    } else { this.shake.x = 0; this.shake.y = 0; }
  }

  // --- PLAYER UPDATE ---
  _updatePlayer(dt) {
    const dx = this.player.tx - this.player.x, dy = this.player.ty - this.player.y;
    this.player.x += dx * 0.09; this.player.y += dy * 0.09;
    this.player.invuln = Math.max(0, this.player.invuln - dt);
    this.player.pulseCd = Math.max(0, this.player.pulseCd - dt);
    if (this.mult.regen > 0) this.player.hp = Math.min(this.player.maxHp, this.player.hp + this.mult.regen * dt / 1000);
    if (this.comboTimer > 0) { this.comboTimer -= dt; if (this.comboTimer <= 0) this.combo = 0; }
    this.cam.x = this.player.x - this.w / 2;
    this.cam.y = this.player.y - this.h / 2;
  }

  // --- MAIN UPDATE ---
  update(dt) {
    if (this.state === 'menu') { this._updateMenu(dt); return; }
    if (this.state === 'gameover') { this._updateFx(dt); return; }
    if (this.state === 'upgrade') { this._updateBoids(dt); this._updateFx(dt); this._updatePickups(dt); return; }
    this.time += dt / 1000;
    this._updatePlayer(dt);
    this._updateBoids(dt);
    this._updateEnemies(dt);
    this._updateWaves(dt);
    this._updatePickups(dt);
    this._updateFx(dt);
  }

  // ============================================================
  // RENDERING
  // ============================================================
  render() {
    const { ctx } = this;
    ctx.fillStyle = C.BG;
    ctx.fillRect(0, 0, this.w, this.h);

    if (this.state === 'menu') { this._drawMenu(ctx); return; }

    ctx.save();
    ctx.translate(-this.cam.x + this.shake.x, -this.cam.y + this.shake.y);
    this._drawGrid(ctx);
    this._drawPulses(ctx);
    this._drawPickups(ctx);
    this._drawAgents(ctx);
    this._drawEnemies(ctx);
    this._drawPlayer(ctx);
    this._drawParticles(ctx);
    this._drawDmgNums(ctx);
    ctx.restore();

    this._drawHUD(ctx);
    if (this.state === 'gameover') this._drawGameOver(ctx);
  }

  _drawGrid(ctx) {
    const s = C.GRID_SIZE;
    const sx = Math.floor(this.cam.x / s) * s;
    const sy = Math.floor(this.cam.y / s) * s;
    ctx.strokeStyle = C.GRID_COLOR; ctx.lineWidth = 1;
    ctx.beginPath();
    for (let x = sx; x < this.cam.x + this.w + s; x += s) { ctx.moveTo(x, this.cam.y); ctx.lineTo(x, this.cam.y + this.h); }
    for (let y = sy; y < this.cam.y + this.h + s; y += s) { ctx.moveTo(this.cam.x, y); ctx.lineTo(this.cam.x + this.w, y); }
    ctx.stroke();
  }

  _drawPulses(ctx) {
    for (const p of this.pulses) {
      const a = p.life / p.maxLife;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(0,229,255,${a * 0.7})`; ctx.lineWidth = 3 * a; ctx.stroke();
      ctx.fillStyle = `rgba(0,229,255,${a * 0.08})`; ctx.fill();
    }
  }

  _drawPickups(ctx) {
    const t = Date.now();
    for (const p of this.pickups) {
      const pulse = 1 + Math.sin(t * 0.006) * 0.25;
      const a = Math.min(1, p.life / 2000);
      ctx.save(); ctx.globalAlpha = a;
      ctx.shadowColor = `hsl(${p.hue},100%,60%)`; ctx.shadowBlur = 10;
      ctx.fillStyle = `hsl(${p.hue},100%,70%)`;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r * pulse, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
    }
  }

  _drawAgents(ctx) {
    for (const ag of this.agents) {
      // trail
      if (ag.trail.length > 1) {
        ctx.beginPath(); ctx.moveTo(ag.trail[0].x, ag.trail[0].y);
        for (let i = 1; i < ag.trail.length; i++) ctx.lineTo(ag.trail[i].x, ag.trail[i].y);
        ctx.strokeStyle = `hsla(${ag.hue},100%,70%,0.15)`; ctx.lineWidth = 2; ctx.stroke();
      }
      // body
      ctx.save();
      ctx.shadowColor = `hsl(${ag.hue},100%,60%)`; ctx.shadowBlur = 8;
      ctx.fillStyle = `hsl(${ag.hue},100%,65%)`;
      ctx.beginPath(); ctx.arc(ag.x, ag.y, ag.r, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
      // hp
      if (ag.hp < ag.maxHp) {
        const bw = ag.r * 3, bx = ag.x - bw / 2, by = ag.y - ag.r - 5;
        ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.fillRect(bx, by, bw, 2);
        ctx.fillStyle = '#69f0ae'; ctx.fillRect(bx, by, bw * (ag.hp / ag.maxHp), 2);
      }
    }
  }

  _drawEnemies(ctx) {
    const t = Date.now();
    for (const e of this.enemies) {
      if (e.dead) continue;
      const col = e.flash > 0 ? '#fff' : e.color;
      ctx.save(); ctx.shadowColor = col; ctx.shadowBlur = 10;

      if (e.type === 'fast') {
        const a = Math.atan2(e.vy, e.vx);
        ctx.fillStyle = col; ctx.beginPath();
        ctx.moveTo(e.x + Math.cos(a) * e.r * 1.5, e.y + Math.sin(a) * e.r * 1.5);
        ctx.lineTo(e.x + Math.cos(a + 2.5) * e.r, e.y + Math.sin(a + 2.5) * e.r);
        ctx.lineTo(e.x + Math.cos(a - 2.5) * e.r, e.y + Math.sin(a - 2.5) * e.r);
        ctx.closePath(); ctx.fill();
      } else if (e.type === 'boss') {
        ctx.fillStyle = col; ctx.beginPath();
        for (let i = 0; i < 6; i++) { const a = (Math.PI / 3) * i + t * 0.001; const px = e.x + Math.cos(a) * e.r; const py = e.y + Math.sin(a) * e.r; i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py); }
        ctx.closePath(); ctx.fill();
        ctx.fillStyle = 'rgba(255,255,255,0.25)'; ctx.beginPath(); ctx.arc(e.x, e.y, e.r * 0.4, 0, Math.PI * 2); ctx.fill();
      } else {
        ctx.fillStyle = col; ctx.beginPath(); ctx.arc(e.x, e.y, e.r, 0, Math.PI * 2); ctx.fill();
        if (e.type === 'tank') { ctx.strokeStyle = 'rgba(255,255,255,0.35)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(e.x, e.y, e.r * 0.6, 0, Math.PI * 2); ctx.stroke(); }
        if (e.type === 'splitter') {
          ctx.strokeStyle = 'rgba(0,0,0,0.3)'; ctx.lineWidth = 2; ctx.beginPath();
          ctx.moveTo(e.x - e.r * 0.5, e.y); ctx.lineTo(e.x + e.r * 0.5, e.y);
          ctx.moveTo(e.x, e.y - e.r * 0.5); ctx.lineTo(e.x, e.y + e.r * 0.5); ctx.stroke();
        }
      }
      ctx.restore();
      // hp bar
      if (e.hp < e.maxHp) {
        const bw = e.r * 2.5, bx = e.x - bw / 2, by = e.y - e.r - 8;
        ctx.fillStyle = 'rgba(0,0,0,0.6)'; ctx.fillRect(bx, by, bw, 3);
        ctx.fillStyle = e.color; ctx.fillRect(bx, by, bw * (e.hp / e.maxHp), 3);
      }
    }
  }

  _drawPlayer(ctx) {
    const p = this.player;
    const pulse = 1 + Math.sin(Date.now() * 0.003) * 0.1;
    ctx.save();
    if (p.invuln > 0) ctx.globalAlpha = 0.5 + Math.sin(Date.now() * 0.02) * 0.3;

    // glow
    const grad = ctx.createRadialGradient(p.x, p.y, p.r * 0.4, p.x, p.y, p.r * 2.8 * pulse);
    grad.addColorStop(0, 'rgba(0,229,255,0.25)'); grad.addColorStop(1, 'rgba(0,229,255,0)');
    ctx.fillStyle = grad; ctx.beginPath(); ctx.arc(p.x, p.y, p.r * 2.8 * pulse, 0, Math.PI * 2); ctx.fill();

    // core
    ctx.shadowColor = C.PLAYER_COLOR; ctx.shadowBlur = 22;
    ctx.fillStyle = C.PLAYER_COLOR; ctx.beginPath(); ctx.arc(p.x, p.y, p.r * pulse, 0, Math.PI * 2); ctx.fill();

    // highlight
    ctx.fillStyle = 'rgba(255,255,255,0.45)'; ctx.beginPath(); ctx.arc(p.x - p.r * 0.3, p.y - p.r * 0.3, p.r * 0.35, 0, Math.PI * 2); ctx.fill();

    ctx.shadowBlur = 0;
    // pulse cd ring
    const cd = C.PULSE_CD * this.mult.pulseCd;
    if (p.pulseCd > 0) {
      const prog = 1 - p.pulseCd / cd;
      ctx.strokeStyle = 'rgba(0,229,255,0.35)'; ctx.lineWidth = 2.5;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r + 9, -Math.PI / 2, -Math.PI / 2 + prog * Math.PI * 2); ctx.stroke();
    } else {
      ctx.strokeStyle = `rgba(0,229,255,${0.4 + Math.sin(Date.now() * 0.005) * 0.3})`;
      ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(p.x, p.y, p.r + 9, 0, Math.PI * 2); ctx.stroke();
    }
    ctx.restore();
  }

  _drawParticles(ctx) {
    for (const p of this.particles) {
      const a = p.life / p.maxLife;
      ctx.globalAlpha = a; ctx.fillStyle = p.color;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r * a, 0, Math.PI * 2); ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  _drawDmgNums(ctx) {
    for (const d of this.dmgNums) {
      const a = d.life / d.maxLife;
      ctx.globalAlpha = a; ctx.fillStyle = d.color;
      ctx.font = `bold 13px "JetBrains Mono",monospace`; ctx.textAlign = 'center';
      ctx.fillText(d.val, d.x, d.y);
    }
    ctx.globalAlpha = 1;
  }

  _drawHUD(ctx) {
    const p = this.player;

    // HP bar
    const bw = 200, bh = 11, bx = 20, by = 20;
    ctx.fillStyle = 'rgba(0,0,0,0.6)'; ctx.fillRect(bx - 1, by - 1, bw + 2, bh + 2);
    ctx.fillStyle = '#111'; ctx.fillRect(bx, by, bw, bh);
    const hr = p.hp / p.maxHp;
    ctx.fillStyle = hr > 0.5 ? '#69f0ae' : hr > 0.25 ? '#ffd740' : '#ff1744';
    ctx.fillRect(bx, by, bw * hr, bh);
    ctx.fillStyle = '#fff'; ctx.font = '9px "JetBrains Mono",monospace'; ctx.textAlign = 'center';
    ctx.fillText(`${Math.round(p.hp)} / ${p.maxHp}`, bx + bw / 2, by + 9);

    // XP bar
    const xpy = by + bh + 6;
    ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.fillRect(bx - 1, xpy - 1, bw + 2, 5);
    ctx.fillStyle = '#111'; ctx.fillRect(bx, xpy, bw, 3);
    ctx.fillStyle = '#00e5ff'; ctx.fillRect(bx, xpy, bw * (this.xp / this.xpNeed), 3);

    // Score
    ctx.textAlign = 'right'; ctx.fillStyle = '#fff';
    ctx.font = 'bold 22px "JetBrains Mono",monospace';
    ctx.fillText(this.score.toLocaleString(), this.w - 20, 34);
    // High score
    if (this.highScore > 0) {
      ctx.font = '10px "JetBrains Mono",monospace'; ctx.fillStyle = '#666';
      ctx.fillText(`BEST: ${this.highScore.toLocaleString()}`, this.w - 20, 50);
    }
    // Wave
    ctx.font = '13px "JetBrains Mono",monospace'; ctx.fillStyle = '#aaa';
    ctx.fillText(`WAVE ${this.wave}`, this.w - 20, 66);

    // Swarm count & level
    ctx.textAlign = 'left';
    ctx.fillStyle = '#00e5ff'; ctx.font = '11px "JetBrains Mono",monospace';
    ctx.fillText(`SWARM: ${this.agents.length}`, 20, xpy + 18);
    ctx.fillStyle = '#ffd740'; ctx.fillText(`LVL ${this.level}`, 120, xpy + 18);

    // Combo
    if (this.combo > 1) {
      ctx.textAlign = 'center';
      ctx.fillStyle = `hsl(${(this.combo * 25) % 360},100%,70%)`;
      ctx.font = `bold ${14 + Math.min(this.combo, 18)}px "JetBrains Mono",monospace`;
      ctx.fillText(`${this.combo}x COMBO`, this.w / 2, this.h - 50);
    }

    // Time
    ctx.textAlign = 'right'; ctx.fillStyle = '#555'; ctx.font = '10px "JetBrains Mono",monospace';
    const m = Math.floor(this.time / 60), s = Math.floor(this.time % 60);
    ctx.fillText(`${m}:${String(s).padStart(2, '0')}`, this.w - 20, 82);

    // Pulse hint
    if (this.player.pulseCd <= 0) {
      ctx.textAlign = 'center';
      ctx.fillStyle = `rgba(0,229,255,${0.4 + Math.sin(Date.now() * 0.005) * 0.3})`;
      ctx.font = '10px "JetBrains Mono",monospace';
      ctx.fillText('CLICK / SPACE \u2014 PULSE', this.w / 2, 22);
    }
  }

  _drawMenu(ctx) {
    // swarm
    for (const a of this.menuSwarm) {
      ctx.save(); ctx.shadowColor = `hsl(${a.hue},100%,60%)`; ctx.shadowBlur = 8;
      ctx.fillStyle = `hsl(${a.hue},100%,65%)`; ctx.beginPath(); ctx.arc(a.x, a.y, a.r, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
    }
    // connecting lines
    ctx.strokeStyle = 'rgba(0,229,255,0.04)'; ctx.lineWidth = 1;
    for (let i = 0; i < this.menuSwarm.length; i++) {
      for (let j = i + 1; j < this.menuSwarm.length; j++) {
        const d = dist(this.menuSwarm[i], this.menuSwarm[j]);
        if (d < 80) { ctx.beginPath(); ctx.moveTo(this.menuSwarm[i].x, this.menuSwarm[i].y); ctx.lineTo(this.menuSwarm[j].x, this.menuSwarm[j].y); ctx.stroke(); }
      }
    }

    ctx.textAlign = 'center';
    // shadow title
    ctx.shadowColor = '#00e5ff'; ctx.shadowBlur = 40;
    ctx.fillStyle = '#00e5ff'; ctx.font = 'bold 58px "Space Grotesk","JetBrains Mono",monospace';
    ctx.fillText('SWARM MIND', this.w / 2, this.h / 2 - 55);
    ctx.shadowBlur = 0;

    ctx.fillStyle = '#888'; ctx.font = '16px "Space Grotesk","JetBrains Mono",monospace';
    ctx.fillText('Guide the hive. Survive the onslaught.', this.w / 2, this.h / 2 - 15);

    const al = 0.4 + Math.sin(Date.now() * 0.003) * 0.5;
    ctx.fillStyle = `rgba(255,255,255,${al})`; ctx.font = '18px "JetBrains Mono",monospace';
    ctx.fillText('[ CLICK TO START ]', this.w / 2, this.h / 2 + 35);

    ctx.fillStyle = '#444'; ctx.font = '12px "JetBrains Mono",monospace';
    ctx.fillText('Move: Mouse  \u2502  Attack: Click / Space  \u2502  Sound: M', this.w / 2, this.h / 2 + 80);
    ctx.fillText('Your swarm fights automatically!', this.w / 2, this.h / 2 + 100);

    if (this.highScore > 0) {
      ctx.fillStyle = '#ffd740'; ctx.font = '13px "JetBrains Mono",monospace';
      ctx.fillText(`HIGH SCORE: ${this.highScore.toLocaleString()}`, this.w / 2, this.h / 2 + 135);
    }
  }

  _drawGameOver(ctx) {
    ctx.fillStyle = 'rgba(0,0,0,0.7)'; ctx.fillRect(0, 0, this.w, this.h);
    ctx.textAlign = 'center';
    ctx.shadowColor = '#ff1744'; ctx.shadowBlur = 25;
    ctx.fillStyle = '#ff1744'; ctx.font = 'bold 44px "Space Grotesk","JetBrains Mono",monospace';
    ctx.fillText('SWARM DESTROYED', this.w / 2, this.h / 2 - 75);
    ctx.shadowBlur = 0;

    ctx.fillStyle = '#fff'; ctx.font = '20px "JetBrains Mono",monospace';
    ctx.fillText(`Score: ${this.score.toLocaleString()}`, this.w / 2, this.h / 2 - 20);

    if (this.score >= this.highScore && this.score > 0) {
      ctx.fillStyle = '#ffd740'; ctx.font = 'bold 14px "JetBrains Mono",monospace';
      ctx.fillText('NEW HIGH SCORE!', this.w / 2, this.h / 2 + 5);
    }

    ctx.fillStyle = '#aaa'; ctx.font = '14px "JetBrains Mono",monospace';
    ctx.fillText(`Wave ${this.wave}  |  ${this.kills} kills  |  Level ${this.level}`, this.w / 2, this.h / 2 + 30);
    const m = Math.floor(this.time / 60), s = Math.floor(this.time % 60);
    ctx.fillText(`Time: ${m}:${String(s).padStart(2, '0')}`, this.w / 2, this.h / 2 + 55);

    const al = 0.4 + Math.sin(Date.now() * 0.003) * 0.5;
    ctx.fillStyle = `rgba(255,255,255,${al})`; ctx.font = '16px "JetBrains Mono",monospace';
    ctx.fillText('[ CLICK TO PLAY AGAIN ]', this.w / 2, this.h / 2 + 95);
  }

  // --- GAME LOOP ---
  _loop() {
    if (!this.running) return;
    const now = performance.now();
    let dt = now - this.lastT;
    this.lastT = now;
    if (dt > 80) dt = 80;
    this.update(dt);
    this.render();
    this.raf = requestAnimationFrame(this._loop);
  }
}
