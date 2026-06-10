/* ============================================================
   ui.jsx — shared primitives + GameContext for Skyfall app
   ============================================================ */
const { useState, useEffect, useRef, useContext, createContext, useCallback } = React;

/* ---------- Context ---------- */
const GameContext = createContext(null);
const useGame = () => useContext(GameContext);

/* ---------- Icons (simple geometric line icons) ---------- */
function Icon({ name, size = 22, stroke = 'currentColor', sw = 1.6 }) {
  const p = { width: size, height: size, viewBox: '0 0 24 24', fill: 'none',
    stroke, strokeWidth: sw, strokeLinecap: 'round', strokeLinejoin: 'round' };
  switch (name) {
    case 'ficha': return (<svg {...p}><rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6M9 12h6M9 16h3"/></svg>);
    case 'inv': return (<svg {...p}><path d="M7 8V6a5 5 0 0 1 10 0v2"/><rect x="4" y="8" width="16" height="12" rx="2"/><path d="M12 12v3"/></svg>);
    case 'cena': return (<svg {...p}><path d="M5 4l9 9M14.5 8.5L20 3M5 20l5.5-5.5M15 15l5 5"/><path d="M3.5 5.5L5 4l1.5 1.5M20.5 18.5L19 20l-1.5-1.5"/></svg>);
    case 'oraculo': return (<svg {...p}><path d="M4 5h16v11H9l-4 4v-4H4z"/><path d="M8.5 10.5h.01M12 10.5h.01M15.5 10.5h.01"/></svg>);
    case 'plus': return (<svg {...p}><path d="M12 6v12M6 12h12"/></svg>);
    case 'minus': return (<svg {...p}><path d="M6 12h12"/></svg>);
    case 'chevron': return (<svg {...p}><path d="M6 9l6 6 6-6"/></svg>);
    case 'die': return (<svg {...p}><rect x="4" y="4" width="16" height="16" rx="3"/><circle cx="9" cy="9" r="1" fill={stroke} stroke="none"/><circle cx="15" cy="15" r="1" fill={stroke} stroke="none"/><circle cx="12" cy="12" r="1" fill={stroke} stroke="none"/></svg>);
    case 'send': return (<svg {...p}><path d="M5 12l14-7-5 16-4-7-5-2z"/></svg>);
    case 'logout': return (<svg {...p}><path d="M14 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2v-2M10 12h10m0 0l-3-3m3 3l-3 3"/></svg>);
    case 'spark': return (<svg {...p}><path d="M12 3l1.6 5.8L19 10l-5.4 1.2L12 17l-1.6-5.8L5 10l5.4-1.2z"/></svg>);
    case 'bolt': return (<svg {...p}><path d="M13 3L5 13h5l-1 8 8-10h-5z"/></svg>);
    case 'skull': return (<svg {...p}><path d="M12 3a8 8 0 0 0-8 8c0 3 1.5 4.5 3 5.5V20h10v-3.5c1.5-1 3-2.5 3-5.5a8 8 0 0 0-8-8z"/><circle cx="9" cy="11" r="1.4"/><circle cx="15" cy="11" r="1.4"/></svg>);
    default: return null;
  }
}

/* arcane sigil mark */
function Sigil({ size = 56, glow = true }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none"
      style={{ filter: glow ? 'drop-shadow(0 0 14px var(--arc-glow))' : 'none' }}>
      <path d="M32 4 56 18v28L32 60 8 46V18z" stroke="var(--arc)" strokeWidth="1.4" opacity="0.55"/>
      <path d="M32 14 47 23v18L32 50 17 41V23z" stroke="var(--arc)" strokeWidth="1.4"/>
      <path d="M32 24v16M24 28l16 8M40 28l-16 8" stroke="var(--arc)" strokeWidth="1.2" opacity="0.8"/>
      <circle cx="32" cy="32" r="3.2" fill="var(--arc)"/>
    </svg>
  );
}

/* ---------- Section label ---------- */
function SectionLabel({ idx, name, accent }) {
  return (
    <div className="seclabel" style={{ marginBottom: 11 }}>
      <span className="idx" style={accent ? { color: accent } : null}>{idx}</span>
      <span className="name">{name}</span>
      <span className="rule" />
    </div>
  );
}

/* ---------- Panel with HUD corners ---------- */
function Panel({ children, corners = true, style, className = '', ...rest }) {
  return (
    <div className={`panel ${className}`} style={style} {...rest}>
      {corners && (<>
        <span className="corner tl" /><span className="corner tr" />
        <span className="corner bl" /><span className="corner br" />
      </>)}
      {children}
    </div>
  );
}

/* ---------- Accordion ---------- */
function Accordion({ idx, title, accent, defaultOpen = false, summary, children }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="panel" style={{ marginBottom: 12, overflow: 'hidden' }}>
      <span className="corner tl" /><span className="corner tr" />
      <span className="corner bl" /><span className="corner br" />
      <button onClick={() => setOpen(o => !o)}
        style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 11,
          padding: '14px 14px', textAlign: 'left' }}>
        <span className="mono" style={{ fontSize: 12, fontWeight: 600, color: accent || 'var(--arc)' }}>{idx}</span>
        <span style={{ flex: 1 }}>
          <span style={{ display: 'block', fontSize: 13.5, letterSpacing: '0.16em',
            textTransform: 'uppercase', color: 'var(--ink)', fontWeight: 500 }}>{title}</span>
          {summary && <span className="mono" style={{ fontSize: 10.5, color: 'var(--ink-3)', letterSpacing: '0.04em' }}>{summary}</span>}
        </span>
        <span style={{ transform: open ? 'rotate(180deg)' : 'none', transition: 'transform .25s ease', color: 'var(--ink-3)', display: 'flex' }}>
          <Icon name="chevron" size={18} />
        </span>
      </button>
      <div style={{ display: 'grid', gridTemplateRows: open ? '1fr' : '0fr', transition: 'grid-template-rows .28s ease' }}>
        <div style={{ overflow: 'hidden' }}>
          <div style={{ padding: '2px 14px 16px', borderTop: '1px solid var(--line)' }}>{children}</div>
        </div>
      </div>
    </div>
  );
}

/* ---------- Counter (+/-) ---------- */
function Counter({ value, set, min = 0, max = 999, accent = 'var(--arc)', size = 'md' }) {
  const big = size === 'lg';
  const btn = (dir, icon) => (
    <button className="tap" onClick={() => set(Math.max(min, Math.min(max, value + dir)))}
      style={{ width: big ? 38 : 32, height: big ? 38 : 32, borderRadius: 7,
        border: '1px solid var(--line-2)', background: 'var(--panel-3)',
        color: 'var(--ink-2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <Icon name={icon} size={big ? 18 : 16} />
    </button>
  );
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
      {btn(-1, 'minus')}
      <span className="mono" style={{ minWidth: big ? 44 : 30, textAlign: 'center',
        fontSize: big ? 26 : 18, fontWeight: 600, color: accent }}>{value}</span>
      {btn(+1, 'plus')}
    </div>
  );
}

/* ---------- Pip row (catarse / ênfase dots) ---------- */
function PipRow({ total, filled, color = 'var(--arc)', onToggle, size = 16 }) {
  return (
    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
      {Array.from({ length: total }).map((_, i) => {
        const on = i < filled;
        return (
          <button key={i} className="tap" onClick={() => onToggle && onToggle(i)}
            style={{ width: size, height: size, borderRadius: '50%',
              border: `1.5px solid ${on ? color : 'var(--line-3)'}`,
              background: on ? color : 'transparent',
              boxShadow: on ? `0 0 8px -1px ${color}` : 'none', transition: 'all .15s ease' }} />
        );
      })}
    </div>
  );
}

/* ---------- Meter bar ---------- */
function Bar({ value, max, color = 'var(--arc)', height = 8, warnOver = false }) {
  const pct = Math.max(0, Math.min(100, max ? (value / max) * 100 : 0));
  const over = value > max;
  const c = over && warnOver ? 'var(--blood)' : color;
  return (
    <div style={{ height, borderRadius: 999, background: 'var(--panel-3)',
      border: '1px solid var(--line)', overflow: 'hidden' }}>
      <div style={{ width: `${pct}%`, height: '100%', background: c,
        boxShadow: `0 0 12px -2px ${c}`, borderRadius: 999, transition: 'width .35s cubic-bezier(.2,.7,.3,1)' }} />
    </div>
  );
}

/* ---------- Death / track checkboxes ---------- */
function TrackBoxes({ count, filled, color = 'var(--blood)', onToggle, glyph }) {
  return (
    <div style={{ display: 'flex', gap: 7 }}>
      {Array.from({ length: count }).map((_, i) => {
        const on = i < filled;
        return (
          <button key={i} className="tap" onClick={() => onToggle(i)}
            style={{ width: 26, height: 26, borderRadius: 6,
              border: `1.5px solid ${on ? color : 'var(--line-3)'}`,
              background: on ? `${color}22` : 'transparent',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color, transition: 'all .15s ease' }}>
            {on && (glyph || <span style={{ width: 9, height: 9, borderRadius: '50%', background: color, boxShadow: `0 0 8px ${color}` }} />)}
          </button>
        );
      })}
    </div>
  );
}

/* ---------- Field (label + editable placeholder) ---------- */
function Field({ label, placeholder, value, onChange, accent }) {
  return (
    <label style={{ display: 'block' }}>
      <span className="micro" style={{ display: 'block', marginBottom: 5, color: accent || 'var(--ink-3)' }}>{label}</span>
      <input value={value || ''} placeholder={placeholder} onChange={e => onChange && onChange(e.target.value)}
        style={{ width: '100%', background: 'var(--panel-3)', border: '1px solid var(--line)',
          borderRadius: 7, padding: '10px 11px', color: 'var(--ink)', fontSize: 14,
          outline: 'none', transition: 'border-color .15s ease' }}
        onFocus={e => e.target.style.borderColor = 'var(--line-3)'}
        onBlur={e => e.target.style.borderColor = 'var(--line)'} />
    </label>
  );
}

/* ---------- Stat tile ---------- */
function StatTile({ label, value, sub, accent = 'var(--ink)', onClick }) {
  return (
    <div className={onClick ? 'tap' : ''} onClick={onClick}
      style={{ background: 'var(--panel-3)', border: '1px solid var(--line)', borderRadius: 8,
        padding: '11px 10px', textAlign: 'center' }}>
      <div className="micro" style={{ marginBottom: 4 }}>{label}</div>
      <div className="mono" style={{ fontSize: 22, fontWeight: 600, color: accent, lineHeight: 1 }}>{value}</div>
      {sub && <div className="mono" style={{ fontSize: 9.5, color: 'var(--ink-3)', marginTop: 4, letterSpacing: '0.08em' }}>{sub}</div>}
    </div>
  );
}

Object.assign(window, { GameContext, useGame, Icon, Sigil, SectionLabel, Panel,
  Accordion, Counter, PipRow, Bar, TrackBoxes, Field, StatTile });
