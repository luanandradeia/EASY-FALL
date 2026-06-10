/* ============================================================
   cena.jsx — Tela de Modo Cena (Dashboard Tático) + rolagens
   ============================================================ */
(function () {
const { useState, useRef } = React;
const { useGame, Icon, Panel, Bar, SectionLabel } = window;

const d = (n) => Math.floor(Math.random() * n) + 1;
const CAMADAS = { Superficial: 'var(--arc)', Rasa: 'var(--sombra)', Profunda: 'var(--blood)' };

function rollFormula(rawDie) {
  // "1d8" -> {rolls:[..], sum}
  const m = /^(\d+)d(\d+)$/.exec(rawDie);
  if (!m) return { rolls: [], sum: 0 };
  const n = +m[1], faces = +m[2];
  const rolls = Array.from({ length: n }, () => d(faces));
  return { rolls, sum: rolls.reduce((a, b) => a + b, 0), faces };
}

function CenaScreen() {
  const { char, patch } = useGame();
  const [result, setResult] = useState(null);
  const [mode, setMode] = useState('normal'); // normal | adv | dis
  const [log, setLog] = useState([]);

  const pushResult = (r) => { setResult(r); setLog(l => [{ ...r, t: Date.now() }, ...l].slice(0, 8)); };

  const rollTest = (label, mod) => {
    let dieRolls = [d(20)];
    if (mode !== 'normal') { dieRolls.push(d(20)); }
    const chosen = mode === 'adv' ? Math.max(...dieRolls) : mode === 'dis' ? Math.min(...dieRolls) : dieRolls[0];
    const total = chosen + mod;
    pushResult({ kind: 'test', label, formula: `1d20${mod >= 0 ? '+' : ''}${mod}`,
      dieRolls, chosen, mod, total, mode,
      crit: chosen === 20, fumble: chosen === 1 });
  };

  const rollDamage = (label, die, bonus = 0, dtipo = '') => {
    const { rolls, sum } = rollFormula(die);
    pushResult({ kind: 'dmg', label, formula: `${die}${bonus ? '+' + bonus : ''}`, rolls, sum: sum + bonus, dtipo });
  };

  const fmt = (n) => (n >= 0 ? '+' : '') + n;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* ---- fixed HUD ---- */}
      <div style={{ flex: '0 0 auto', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10,
        padding: '13px 15px', borderBottom: '1px solid var(--line-2)', background: 'rgba(8,17,18,0.6)' }}>
        <HudStat label="Pontos de Vida" color="var(--blood)"
          atual={char.pv.atual} max={char.pv.max} temp={char.pv.temp}
          dec={() => patch('pv', { atual: Math.max(0, char.pv.atual - 1) })}
          inc={() => patch('pv', { atual: Math.min(char.pv.max + char.pv.temp, char.pv.atual + 1) })} />
        <HudStat label="Ênfase" color="var(--enfase)"
          atual={char.enfase.atual} max={char.enfase.total}
          dec={() => patch('enfase', { atual: Math.max(0, char.enfase.atual - 1) })}
          inc={() => patch('enfase', { atual: Math.min(char.enfase.total, char.enfase.atual + 1) })} />
      </div>

      <div className="screen" style={{ flex: 1 }}>
        <div className="screen-pad">
          {/* advantage toggle */}
          <div style={{ display: 'flex', gap: 6, marginBottom: 14, background: 'var(--panel)', borderRadius: 8,
            border: '1px solid var(--line)', padding: 4 }}>
            {[['dis', 'Desvantagem', 'var(--blood)'], ['normal', 'Normal', 'var(--ink)'], ['adv', 'Vantagem', 'var(--arc)']].map(([k, lbl, col]) => (
              <button key={k} onClick={() => setMode(k)} className="tap"
                style={{ flex: 1, padding: '8px 4px', borderRadius: 6, fontFamily: 'var(--mono)', fontSize: 10,
                  letterSpacing: '0.08em', textTransform: 'uppercase',
                  background: mode === k ? (k === 'normal' ? 'var(--panel-3)' : `${col}1e`) : 'transparent',
                  color: mode === k ? col : 'var(--ink-3)',
                  border: `1px solid ${mode === k && k !== 'normal' ? col : 'transparent'}` }}>{lbl}</button>
            ))}
          </div>

          {/* attribute test macros */}
          <SectionLabel idx="01" name="Testes de Atributo" />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 8, marginBottom: 18 }}>
            {char.attrOrder.map(a => {
              const mod = char.attrs[a] + char.prof;
              return (
                <button key={a} className="tap panel" onClick={() => rollTest(`Teste de ${a}`, char.attrs[a])}
                  style={{ padding: '12px 6px', textAlign: 'center', borderRadius: 8 }}>
                  <div className="mono" style={{ fontSize: 10, letterSpacing: '0.18em', color: 'var(--arc)', fontWeight: 600 }}>{a}</div>
                  <div className="mono" style={{ fontSize: 20, fontWeight: 700, color: 'var(--ink)', marginTop: 3 }}>{fmt(char.attrs[a])}</div>
                  <div className="mono" style={{ fontSize: 8.5, color: 'var(--ink-4)', marginTop: 4, letterSpacing: '0.1em' }}>ROLAR 1d20</div>
                </button>
              );
            })}
          </div>

          {/* skill quick tests */}
          <SectionLabel idx="02" name="Perícias Frequentes" />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 7, marginBottom: 18 }}>
            {char.skills.filter(s => s.prof).map(s => {
              const mod = char.attrs[s.attr] + char.prof;
              return (
                <button key={s.nome} className="tap panel" onClick={() => rollTest(s.nome, mod)}
                  style={{ display: 'flex', alignItems: 'center', gap: 11, padding: '11px 13px', borderRadius: 8, textAlign: 'left' }}>
                  <Icon name="die" size={17} stroke="var(--arc)" />
                  <span style={{ flex: 1, fontSize: 14, color: 'var(--ink)' }}>{s.nome}</span>
                  <span className="mono" style={{ fontSize: 9.5, color: 'var(--ink-4)' }}>{s.attr}</span>
                  <span className="mono" style={{ fontSize: 15, fontWeight: 600, color: 'var(--arc)' }}>{fmt(mod)}</span>
                </button>
              );
            })}
          </div>

          {/* weapons */}
          <SectionLabel idx="03" name="Ataques de Arma" accent="var(--blood)" />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 9, marginBottom: 18 }}>
            {char.itens.filter(i => i.tipo === 'Arma' && i.equipado).map(w => (
              <Panel key={w.id} style={{ padding: '12px 13px' }}>
                <span className="corner tl" /><span className="corner tr" />
                <span className="corner bl" /><span className="corner br" />
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                  <span style={{ fontSize: 14.5, fontWeight: 500, color: 'var(--ink)', flex: 1 }}>{w.nome}</span>
                  <span className="chip" style={{ color: 'var(--blood)', borderColor: 'var(--blood-deep)', background: 'rgba(255,93,108,0.06)' }}>{w.dtipo}</span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                  <button className="tap" onClick={() => rollTest(`Ataque · ${w.nome}`, w.atk)}
                    style={{ padding: '10px', borderRadius: 7, border: '1px solid var(--line-2)', background: 'var(--panel-3)',
                      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
                    <span className="micro">Ataque</span>
                    <span className="mono" style={{ fontSize: 16, fontWeight: 600, color: 'var(--arc)' }}>{fmt(w.atk)}</span>
                  </button>
                  <button className="tap" onClick={() => rollDamage(`Dano · ${w.nome}`, w.dano, 0, w.dtipo)}
                    style={{ padding: '10px', borderRadius: 7, border: '1px solid var(--blood-deep)', background: 'rgba(255,93,108,0.07)',
                      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
                    <span className="micro" style={{ color: 'var(--blood)' }}>Dano</span>
                    <span className="mono" style={{ fontSize: 16, fontWeight: 600, color: 'var(--blood)' }}>{w.dano}</span>
                  </button>
                </div>
              </Panel>
            ))}
          </div>

          {/* grimório */}
          <SectionLabel idx="04" name="Grimório & Habilidades" accent="var(--sombra)" />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 9 }}>
            {['Superficial', 'Rasa', 'Profunda'].map(cam => {
              const spells = char.spells.filter(s => s.camada === cam);
              if (!spells.length) return null;
              return (
                <div key={cam}>
                  <div className="micro" style={{ color: CAMADAS[cam], margin: '4px 0 7px', display: 'flex', alignItems: 'center', gap: 7 }}>
                    <span style={{ width: 6, height: 6, borderRadius: '50%', background: CAMADAS[cam], boxShadow: `0 0 7px ${CAMADAS[cam]}` }} />
                    Camada {cam}
                  </div>
                  {spells.map(s => <SpellCard key={s.id} s={s} onAttack={() => rollTest(`Conjurar · ${s.nome}`, s.atk)} />)}
                </div>
              );
            })}
          </div>

          {/* mini log */}
          {log.length > 0 && (
            <div style={{ marginTop: 20 }}>
              <SectionLabel idx="//" name="Histórico de Rolagens" />
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                {log.map((r, i) => (
                  <div key={r.t} style={{ display: 'flex', alignItems: 'center', gap: 9, padding: '7px 11px',
                    background: 'var(--panel)', border: '1px solid var(--line)', borderRadius: 6, opacity: 1 - i * 0.085 }}>
                    <span className="mono" style={{ fontSize: 11, color: 'var(--ink-3)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.label}</span>
                    <span className="mono" style={{ fontSize: 10, color: 'var(--ink-4)' }}>{r.formula}</span>
                    <span className="mono" style={{ fontSize: 15, fontWeight: 700,
                      color: r.crit ? 'var(--arc)' : r.fumble ? 'var(--blood)' : 'var(--ink)' }}>
                      {r.kind === 'test' ? r.total : r.sum}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {result && <RollOverlay result={result} onClose={() => setResult(null)} />}
    </div>
  );
}

function HudStat({ label, color, atual, max, temp, dec, inc }) {
  return (
    <div style={{ background: 'var(--panel)', border: '1px solid var(--line-2)', borderRadius: 9, padding: '9px 11px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <span className="micro" style={{ color }}>{label}</span>
        <span className="mono" style={{ fontSize: 10, color: 'var(--ink-4)' }}>/ {max}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 5 }}>
        <button className="tap" onClick={dec} style={{ width: 26, height: 26, borderRadius: 6, border: '1px solid var(--line-2)', color: 'var(--ink-2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Icon name="minus" size={15} /></button>
        <span className="mono" style={{ flex: 1, textAlign: 'center', fontSize: 24, fontWeight: 700, color }}>
          {atual}{temp > 0 && <span style={{ fontSize: 13, color: 'var(--arc)' }}> +{temp}</span>}
        </span>
        <button className="tap" onClick={inc} style={{ width: 26, height: 26, borderRadius: 6, border: '1px solid var(--line-2)', color: 'var(--ink-2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Icon name="plus" size={15} /></button>
      </div>
    </div>
  );
}

function SpellCard({ s, onAttack }) {
  const [open, setOpen] = useState(false);
  const col = CAMADAS[s.camada];
  return (
    <div className="panel" style={{ marginBottom: 8, overflow: 'hidden' }}>
      <span className="corner tl" /><span className="corner tr" />
      <span className="corner bl" /><span className="corner br" />
      <button onClick={() => setOpen(o => !o)} style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 10, padding: '11px 13px', textAlign: 'left' }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 14, fontWeight: 500, color: 'var(--ink)' }}>{s.nome}</div>
          <div className="mono" style={{ fontSize: 9.5, color: 'var(--ink-3)', marginTop: 3 }}>
            CHAVE {s.chave} · ALCANCE {s.alcance} · {s.duracao}
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, padding: '3px 7px', borderRadius: 5,
          border: `1px solid ${col}`, background: `${col}14` }}>
          <Icon name="bolt" size={11} stroke={col} />
          <span className="mono" style={{ fontSize: 11, fontWeight: 600, color: col }}>{s.custo}</span>
        </div>
      </button>
      <div style={{ display: 'grid', gridTemplateRows: open ? '1fr' : '0fr', transition: 'grid-template-rows .26s ease' }}>
        <div style={{ overflow: 'hidden' }}>
          <div style={{ padding: '4px 13px 13px', borderTop: '1px solid var(--line)' }}>
            <p style={{ fontSize: 12.5, color: 'var(--ink-2)', lineHeight: 1.55, margin: '10px 0 11px' }}>{s.efeito}</p>
            <button className="tap" onClick={onAttack}
              style={{ width: '100%', padding: '9px', borderRadius: 7, border: `1px solid ${col}`, background: `${col}18`,
                color: col, fontFamily: 'var(--mono)', fontSize: 11, letterSpacing: '0.12em', textTransform: 'uppercase',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 7 }}>
              <Icon name="die" size={15} stroke={col} /> Rolar Ataque {s.atk >= 0 ? '+' : ''}{s.atk}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ---- roll result overlay ---- */
function RollOverlay({ result, onClose }) {
  const r = result;
  const isTest = r.kind === 'test';
  const big = isTest ? r.total : r.sum;
  const accent = r.crit ? 'var(--arc)' : r.fumble ? 'var(--blood)' : 'var(--ink)';
  return (
    <div onClick={onClose} style={{ position: 'absolute', inset: 0, zIndex: 40,
      background: 'rgba(4,9,10,0.78)', backdropFilter: 'blur(4px)', display: 'flex',
      alignItems: 'center', justifyContent: 'center', padding: 30, animation: 'screen-in .18s ease' }}>
      <div onClick={e => e.stopPropagation()} className="panel-2 panel" style={{ width: '100%', maxWidth: 320, padding: '24px 22px', textAlign: 'center', position: 'relative' }}>
        <span className="corner tl" /><span className="corner tr" /><span className="corner bl" /><span className="corner br" />
        <div className="eyebrow" style={{ color: accent }}>{r.label}</div>
        <div className="mono" style={{ fontSize: 11, color: 'var(--ink-4)', marginTop: 6 }}>
          {r.formula}{r.mode && r.mode !== 'normal' ? (r.mode === 'adv' ? ' · VANTAGEM' : ' · DESVANTAGEM') : ''}
        </div>

        <div style={{ margin: '18px 0 6px', animation: 'roll-spin .4s ease' }}>
          <span className="mono" style={{ fontSize: 72, fontWeight: 700, lineHeight: 1, color: accent,
            textShadow: `0 0 30px ${accent}66` }}>{big}</span>
        </div>

        {isTest ? (
          <div className="mono" style={{ fontSize: 12, color: 'var(--ink-3)' }}>
            <span style={{ display: 'inline-flex', gap: 6, flexWrap: 'wrap', justifyContent: 'center' }}>
              {r.dieRolls.map((dr, i) => (
                <span key={i} style={{ padding: '2px 8px', borderRadius: 5, border: '1px solid var(--line-2)',
                  color: dr === r.chosen ? accent : 'var(--ink-4)',
                  background: dr === r.chosen ? `${accent}14` : 'transparent',
                  textDecoration: r.mode !== 'normal' && dr !== r.chosen ? 'line-through' : 'none' }}>d20: {dr}</span>
              ))}
              <span style={{ padding: '2px 8px' }}>{r.mod >= 0 ? '+' : ''}{r.mod}</span>
            </span>
          </div>
        ) : (
          <div className="mono" style={{ fontSize: 12, color: 'var(--ink-3)' }}>
            {r.rolls.join(' + ')}{r.dtipo ? ` · ${r.dtipo}` : ''}
          </div>
        )}

        {r.crit && <div className="mono" style={{ marginTop: 12, fontSize: 11, letterSpacing: '0.2em', color: 'var(--arc)' }}>◆ ACERTO CRÍTICO ◆</div>}
        {r.fumble && <div className="mono" style={{ marginTop: 12, fontSize: 11, letterSpacing: '0.2em', color: 'var(--blood)' }}>✕ FALHA CRÍTICA ✕</div>}

        <button onClick={onClose} className="btn ghost" style={{ marginTop: 20, width: '100%' }}>Fechar</button>
      </div>
    </div>
  );
}

window.CenaScreen = CenaScreen;
})();
