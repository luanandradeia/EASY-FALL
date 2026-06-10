/* ============================================================
   inventario.jsx — Tela de Inventário Funcional
   ============================================================ */
(function () {
const { useState } = React;
const { useGame, Icon, Panel, Counter, Bar, SectionLabel } = window;

const TIPO_COLOR = { Arma: 'var(--blood)', Armadura: 'var(--arc)', Engenhoca: 'var(--sombra)', Consumível: 'var(--catarse)' };

function MeterCard({ label, atual, limite, color, hint }) {
  const over = atual > limite;
  const pct = Math.min(100, (atual / limite) * 100);
  return (
    <Panel style={{ padding: '13px 14px' }}>
      <span className="corner tl" /><span className="corner tr" />
      <span className="corner bl" /><span className="corner br" />
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 9 }}>
        <span className="micro" style={{ color }}>{label}</span>
        <span className="mono" style={{ fontSize: 15, fontWeight: 600, color: over ? 'var(--blood)' : 'var(--ink)' }}>
          {atual}<span style={{ color: 'var(--ink-4)', fontWeight: 400 }}> / {limite}</span>
        </span>
      </div>
      <Bar value={atual} max={limite} color={color} height={9} warnOver={true} />
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 7 }}>
        <span className="mono" style={{ fontSize: 9, color: 'var(--ink-4)', letterSpacing: '0.06em' }}>{hint}</span>
        {over && <span className="mono" style={{ fontSize: 9, color: 'var(--blood)', letterSpacing: '0.1em' }}>SOBRECARGA</span>}
      </div>
    </Panel>
  );
}

function ItemCard({ item }) {
  const { setItems } = useGame();
  const [open, setOpen] = useState(false);
  const color = TIPO_COLOR[item.tipo] || 'var(--arc)';
  const toggleEquip = (e) => { e.stopPropagation();
    setItems(list => list.map(i => i.id === item.id ? { ...i, equipado: !i.equipado } : i)); };
  const setText = (v) => setItems(list => list.map(i => i.id === item.id ? { ...i, texto: v } : i));

  return (
    <div className="panel" style={{ marginBottom: 10, overflow: 'hidden' }}>
      <span className="corner tl" /><span className="corner tr" />
      <span className="corner bl" /><span className="corner br" />
      <button onClick={() => setOpen(o => !o)} style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 11, padding: '12px 13px', textAlign: 'left' }}>
        <span style={{ width: 4, alignSelf: 'stretch', borderRadius: 2, background: color, flexShrink: 0,
          boxShadow: item.equipado ? `0 0 8px -1px ${color}` : 'none', opacity: item.equipado ? 1 : 0.4 }} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 14.5, fontWeight: 500, color: 'var(--ink)' }}>{item.nome}</span>
            {item.equipado && <span className="mono" style={{ fontSize: 8, letterSpacing: '0.14em', color, border: `1px solid ${color}`, borderRadius: 3, padding: '1px 4px' }}>EQP</span>}
          </div>
          <div className="mono" style={{ fontSize: 10, color: 'var(--ink-3)', marginTop: 3, letterSpacing: '0.04em' }}>
            {item.tipo} · VOL {item.vol} · FRAG {item.frag}{item.dano ? ` · ${item.dano} ${item.dtipo}` : ''}
          </div>
        </div>
        <span style={{ transform: open ? 'rotate(180deg)' : 'none', transition: 'transform .25s ease', color: 'var(--ink-3)', display: 'flex' }}>
          <Icon name="chevron" size={17} />
        </span>
      </button>

      <div style={{ display: 'grid', gridTemplateRows: open ? '1fr' : '0fr', transition: 'grid-template-rows .26s ease' }}>
        <div style={{ overflow: 'hidden' }}>
          <div style={{ padding: '4px 13px 14px', borderTop: '1px solid var(--line)' }}>
            {/* metric chips */}
            <div style={{ display: 'flex', gap: 8, margin: '11px 0' }}>
              <Metric label="VOL" value={item.vol} />
              <Metric label="FRAG" value={item.frag} accent={item.frag > 0 ? 'var(--sombra)' : 'var(--ink-3)'} />
              {item.atk != null && <Metric label="ATK" value={'+' + item.atk} accent="var(--blood)" />}
            </div>
            {/* descritores */}
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 11 }}>
              {item.descritores.map(d => <span key={d} className="chip">{d}</span>)}
            </div>
            {/* descriptive text */}
            <div className="micro" style={{ marginBottom: 5 }}>Descritores</div>
            <textarea value={item.texto} onChange={e => setText(e.target.value)} rows={2}
              style={{ width: '100%', background: 'var(--panel-3)', border: '1px solid var(--line)', borderRadius: 7,
                padding: '9px 10px', color: 'var(--ink-2)', fontSize: 12.5, lineHeight: 1.5, outline: 'none', resize: 'none',
                fontFamily: 'var(--sans)' }} />
            <button className="tap" onClick={toggleEquip}
              style={{ marginTop: 11, width: '100%', padding: '9px', borderRadius: 7,
                border: `1px solid ${item.equipado ? color : 'var(--line-2)'}`,
                background: item.equipado ? `${color}1a` : 'transparent', color: item.equipado ? color : 'var(--ink-2)',
                fontFamily: 'var(--mono)', fontSize: 11, letterSpacing: '0.14em', textTransform: 'uppercase' }}>
              {item.equipado ? 'Equipado ✓' : 'Equipar item'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function Metric({ label, value, accent = 'var(--ink)' }) {
  return (
    <div style={{ flex: 1, background: 'var(--panel-3)', border: '1px solid var(--line)', borderRadius: 7, padding: '8px 9px', textAlign: 'center' }}>
      <div className="micro" style={{ marginBottom: 3 }}>{label}</div>
      <div className="mono" style={{ fontSize: 16, fontWeight: 600, color: accent }}>{value}</div>
    </div>
  );
}

function InventarioScreen() {
  const { char, cargaAtual, cargaLimite, fragAtual, fragLimite } = useGame();
  const r = char.riquezas;
  return (
    <div className="screen-pad">
      {/* meters */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 11, marginBottom: 16 }}>
        <MeterCard label="Volume de Carga" atual={cargaAtual} limite={cargaLimite}
          color="var(--arc)" hint={`LIMITE = 8 + FOR×2  (FOR ${char.attrs.FOR})`} />
        <MeterCard label="Fragmentos Arcanos" atual={fragAtual} limite={fragLimite}
          color="var(--sombra)" hint={`LIMITE = CAR + PROF×2  (CAR ${char.attrs.CAR})`} />
      </div>

      {/* riquezas */}
      <Panel style={{ padding: '11px 14px', marginBottom: 18, display: 'flex', alignItems: 'center', gap: 14 }}>
        <span className="corner tl" /><span className="corner tr" />
        <span className="corner bl" /><span className="corner br" />
        <span className="micro" style={{ color: 'var(--catarse)' }}>Riquezas</span>
        <div style={{ flex: 1 }} />
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 5 }}>
          <span className="mono" style={{ fontSize: 18, fontWeight: 600, color: 'var(--catarse)' }}>{r.trocados}</span>
          <span className="mono" style={{ fontSize: 11, color: 'var(--ink-3)' }}>$T</span>
        </div>
        <div style={{ width: 1, height: 22, background: 'var(--line-2)' }} />
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 5 }}>
          <span className="mono" style={{ fontSize: 18, fontWeight: 600, color: 'var(--catarse)' }}>{r.pecas}</span>
          <span className="mono" style={{ fontSize: 11, color: 'var(--ink-3)' }}>$P</span>
        </div>
      </Panel>

      <div style={{ marginBottom: 11 }}>
        <SectionLabel idx="//" name={`Equipamentos · ${char.itens.length}`} />
      </div>
      {char.itens.map(item => <ItemCard key={item.id} item={item} />)}

      <button className="tap" style={{ width: '100%', marginTop: 6, padding: '13px', borderRadius: 8,
        border: '1px dashed var(--line-3)', color: 'var(--ink-3)', display: 'flex', alignItems: 'center',
        justifyContent: 'center', gap: 8, fontFamily: 'var(--mono)', fontSize: 11, letterSpacing: '0.14em', textTransform: 'uppercase' }}>
        <Icon name="plus" size={16} /> Adicionar item
      </button>
    </div>
  );
}

window.InventarioScreen = InventarioScreen;
})();
