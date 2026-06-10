/* ============================================================
   ficha.jsx — Tela de Ficha de Personagem (Mobile-First)
   ============================================================ */
(function () {
const { useState } = React;
const { useGame, Icon, Panel, Accordion, Counter, PipRow, Bar, TrackBoxes, Field, StatTile, SectionLabel } = window;

/* ---- Identity header (fixed-feel card) ---- */
function IdentityHeader() {
  const { char, setField } = useGame();
  const id = char.identidade;
  return (
    <Panel style={{ padding: 0, marginBottom: 16, overflow: 'hidden' }}>
      <span className="corner tl" /><span className="corner tr" />
      <span className="corner bl" /><span className="corner br" />
      <div style={{ display: 'flex', gap: 13, padding: '15px 15px 14px' }}>
        {/* portrait placeholder */}
        <div style={{ width: 72, height: 88, borderRadius: 8, flexShrink: 0, position: 'relative',
          background: 'repeating-linear-gradient(135deg, var(--panel-3) 0 7px, var(--panel-2) 7px 14px)',
          border: '1px solid var(--line-2)', display: 'flex', alignItems: 'flex-end', justifyContent: 'center', overflow: 'hidden' }}>
          <span className="mono" style={{ fontSize: 8, color: 'var(--ink-3)', padding: 4, textAlign: 'center', letterSpacing: '0.06em' }}>RETRATO</span>
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <input value={id.nome} onChange={e => setField('identidade', 'nome', e.target.value)}
            placeholder="Nome da Personagem"
            style={{ width: '100%', background: 'transparent', border: 'none', outline: 'none',
              fontFamily: 'var(--sans)', fontSize: 20, fontWeight: 600, color: 'var(--ink)', letterSpacing: '0.01em' }} />
          <div style={{ display: 'flex', gap: 6, marginTop: 6, flexWrap: 'wrap' }}>
            <input value={id.pronomes} onChange={e => setField('identidade', 'pronomes', e.target.value)}
              placeholder="pronomes"
              style={{ background: 'var(--panel-3)', border: '1px solid var(--line)', borderRadius: 5,
                padding: '3px 7px', fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-2)', width: 92, outline: 'none' }} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 10 }}>
            <MiniField label="Nível" value={id.nivel} onChange={v => setField('identidade', 'nivel', v)} placeholder="—" />
            <MiniField label="Classe" value={id.classe} onChange={v => setField('identidade', 'classe', v)} placeholder="Ocultista" />
          </div>
        </div>
      </div>
      <div style={{ borderTop: '1px solid var(--line)', padding: '9px 15px',
        display: 'flex', alignItems: 'center', gap: 8 }}>
        <span className="micro">Jogadore</span>
        <input value={id.jogadore} onChange={e => setField('identidade', 'jogadore', e.target.value)}
          placeholder="—" style={{ flex: 1, background: 'transparent', border: 'none', outline: 'none',
            fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--ink-2)' }} />
      </div>
    </Panel>
  );
}

function MiniField({ label, value, onChange, placeholder }) {
  return (
    <div>
      <span className="micro" style={{ display: 'block', marginBottom: 3 }}>{label}</span>
      <input value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder}
        style={{ width: '100%', background: 'var(--panel-3)', border: '1px solid var(--line)', borderRadius: 6,
          padding: '6px 8px', fontFamily: 'var(--mono)', fontSize: 12.5, color: 'var(--ink)', outline: 'none' }} />
    </div>
  );
}

/* ---- 01 Origem & Histórico ---- */
function OrigemPanel() {
  const { char, setField } = useGame();
  const o = char.origem;
  return (
    <Accordion idx="01" title="Origem & Histórico" defaultOpen={true}
      summary="Legado · Herança · Antecedente · Maldição">
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, paddingTop: 12 }}>
        <Field label="Legado" placeholder="ex. Humani — Tradição Oral" value={o.legado} onChange={v => setField('origem', 'legado', v)} />
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          <Field label="Herança" placeholder="ex. Mortalha" value={o.heranca} onChange={v => setField('origem', 'heranca', v)} />
          <Field label="Antecedente" placeholder="ex. Agouro" value={o.antecedente} onChange={v => setField('origem', 'antecedente', v)} />
        </div>
        <Field label="Maldição" placeholder="A dívida que te persegue…" value={o.maldicao} onChange={v => setField('origem', 'maldicao', v)} accent="var(--sombra)" />
        {/* Melancolia — narrative mechanic */}
        <div style={{ background: 'var(--panel-3)', border: '1px solid var(--line)', borderRadius: 8, padding: '11px 12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 7 }}>
            <Icon name="spark" size={14} stroke="var(--catarse)" />
            <span className="micro" style={{ color: 'var(--catarse)' }}>Melancolia — gera Catarse</span>
          </div>
          <textarea value={o.melancolia} onChange={e => setField('origem', 'melancolia', e.target.value)}
            placeholder="O luto, a saudade ou o arrependimento que move sua personagem…"
            rows={2} style={{ width: '100%', background: 'transparent', border: 'none', outline: 'none', resize: 'none',
              fontFamily: 'var(--sans)', fontSize: 13, color: 'var(--ink)', lineHeight: 1.5 }} />
        </div>
      </div>
    </Accordion>
  );
}

/* ---- 02 Atributos ---- */
function AtributosPanel() {
  const { char, protecao } = useGame();
  return (
    <Accordion idx="02" title="Atributos" defaultOpen={true}
      summary="Valor base · Proteção (10 + Atr + Prof)">
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 9, paddingTop: 12 }}>
        {char.attrOrder.map(a => {
          const v = char.attrs[a];
          return (
            <div key={a} className="tap panel-2" style={{ position: 'relative', borderRadius: 9,
              border: '1px solid var(--line-2)', padding: '11px 8px 9px', textAlign: 'center', background: 'var(--panel-2)' }}>
              <div className="mono" style={{ fontSize: 10, letterSpacing: '0.2em', color: 'var(--arc)', fontWeight: 600 }}>{a}</div>
              <div className="mono" style={{ fontSize: 30, fontWeight: 700, color: 'var(--ink)', lineHeight: 1.05, marginTop: 2 }}>
                {v >= 0 ? '+' : ''}{v}
              </div>
              <div style={{ marginTop: 7, paddingTop: 7, borderTop: '1px solid var(--line)' }}>
                <div className="micro" style={{ fontSize: 8.5, marginBottom: 1 }}>Proteção</div>
                <div className="mono" style={{ fontSize: 15, fontWeight: 600, color: 'var(--ink-2)' }}>{protecao(a)}</div>
              </div>
            </div>
          );
        })}
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 11, padding: '8px 11px',
        background: 'var(--panel-3)', borderRadius: 7, border: '1px solid var(--line)' }}>
        <span className="micro">Bônus de Proficiência</span>
        <span className="mono" style={{ fontSize: 13, fontWeight: 600, color: 'var(--arc)' }}>+{char.prof}</span>
      </div>
    </Accordion>
  );
}

/* ---- 03 Status Vital ---- */
function StatusVitalPanel() {
  const { char, patch, setChar } = useGame();
  const pv = char.pv, dv = char.dadosVida, cat = char.catarse, enf = char.enfase, som = char.sombra, mor = char.morte;

  const setPip = (key, max) => (i) => {
    setChar(c => {
      const cur = c[key].atual;
      const next = (i + 1 === cur) ? i : i + 1; // tap filled-last to clear
      return { ...c, [key]: { ...c[key], atual: Math.max(0, Math.min(max ?? c[key].total, next)) } };
    });
  };
  const setMorte = (kind) => (i) => {
    setChar(c => {
      const cur = c.morte[kind];
      const next = (i + 1 === cur) ? i : i + 1;
      return { ...c, morte: { ...c.morte, [kind]: Math.max(0, Math.min(3, next)) } };
    });
  };

  return (
    <Accordion idx="03" title="Status Vital" accent="var(--blood)"
      summary="PV · Dados de Vida · Catarse · Ênfase · Morte · Sombra">
      <div style={{ display: 'flex', flexDirection: 'column', gap: 13, paddingTop: 13 }}>

        {/* PV */}
        <div className="panel-2" style={{ borderRadius: 9, border: '1px solid var(--line-2)', padding: '12px 13px', background: 'var(--panel-2)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 9 }}>
            <span className="micro" style={{ color: 'var(--blood)' }}>Pontos de Vida</span>
            <span className="mono" style={{ fontSize: 11, color: 'var(--ink-3)' }}>
              {pv.atual}{pv.temp > 0 && <span style={{ color: 'var(--arc)' }}> +{pv.temp}</span>} / {pv.max}
            </span>
          </div>
          <Bar value={pv.atual} max={pv.max} color="var(--blood)" height={9} />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 12 }}>
            <span className="micro">Atual</span>
            <Counter value={pv.atual} set={v => patch('pv', { atual: v })} min={0} max={pv.max + pv.temp} accent="var(--blood)" size="lg" />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 10,
            paddingTop: 10, borderTop: '1px solid var(--line)' }}>
            <span className="micro">PV Temporário</span>
            <Counter value={pv.temp} set={v => patch('pv', { temp: v })} min={0} max={99} accent="var(--arc)" />
          </div>
        </div>

        {/* Dados de vida + Riquezas-style row */}
        <div className="panel-2" style={{ borderRadius: 9, border: '1px solid var(--line-2)', padding: '12px 13px', background: 'var(--panel-2)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div className="micro" style={{ marginBottom: 2 }}>Dados de Vida</div>
              <div className="mono" style={{ fontSize: 12, color: 'var(--ink-3)' }}>
                {dv.total - dv.usados} disponíveis · {dv.total} totais
              </div>
            </div>
            <Counter value={dv.usados} set={v => patch('dadosVida', { usados: v })} min={0} max={dv.total} accent="var(--ink)" />
          </div>
          <div style={{ display: 'flex', gap: 5, marginTop: 11 }}>
            {Array.from({ length: dv.total }).map((_, i) => (
              <span key={i} style={{ flex: 1, height: 6, borderRadius: 3,
                background: i < dv.total - dv.usados ? 'var(--arc)' : 'var(--panel-3)',
                boxShadow: i < dv.total - dv.usados ? '0 0 8px -2px var(--arc)' : 'none',
                border: '1px solid var(--line)' }} />
            ))}
          </div>
        </div>

        {/* Catarse + Ênfase */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 11 }}>
          <ResourceBox label="Catarse" max="5" color="var(--catarse)" icon="spark"
            total={cat.total} atual={cat.atual} onPip={setPip('catarse', 5)}
            onTotal={v => patch('catarse', { total: Math.max(cat.atual, v) })} cap={5} />
          <ResourceBox label="Ênfase" color="var(--enfase)" icon="bolt"
            total={enf.total} atual={enf.atual} onPip={setPip('enfase')}
            onTotal={v => patch('enfase', { total: Math.max(enf.atual, v) })} cap={9} />
        </div>

        {/* Testes de Morte */}
        <div className="panel-2" style={{ borderRadius: 9, border: '1px solid var(--line-2)', padding: '12px 13px', background: 'var(--panel-2)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 11 }}>
            <Icon name="skull" size={15} stroke="var(--blood)" />
            <span className="micro" style={{ color: 'var(--blood)' }}>Testes de Morte</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 9 }}>
            <span className="micro" style={{ color: 'var(--arc)' }}>Sucessos</span>
            <TrackBoxes count={3} filled={mor.sucesso} color="var(--arc)" onToggle={setMorte('sucesso')} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="micro" style={{ color: 'var(--blood)' }}>Falhas</span>
            <TrackBoxes count={3} filled={mor.falha} color="var(--blood)" onToggle={setMorte('falha')}
              glyph={<Icon name="skull" size={13} stroke="var(--blood)" />} />
          </div>
        </div>

        {/* Sombra track */}
        <div className="panel-2" style={{ borderRadius: 9, border: '1px solid var(--sombra-deep)', padding: '12px 13px',
          background: 'linear-gradient(180deg, var(--panel-2), rgba(46,33,80,0.15))' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 10 }}>
            <span className="micro" style={{ color: 'var(--sombra)' }}>Pontos de Sombra — corrupção arcana</span>
            <span className="mono" style={{ fontSize: 11, color: 'var(--sombra)' }}>{som.atual}/{som.total}</span>
          </div>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {Array.from({ length: som.total }).map((_, i) => {
              const on = i < som.atual;
              return (
                <button key={i} className="tap" onClick={() => setPip('sombra')(i)}
                  style={{ width: 24, height: 24, borderRadius: 5, transform: 'rotate(45deg)',
                    border: `1.5px solid ${on ? 'var(--sombra)' : 'var(--line-3)'}`,
                    background: on ? 'var(--sombra)' : 'transparent',
                    boxShadow: on ? '0 0 9px -1px var(--sombra)' : 'none', transition: 'all .15s ease' }} />
              );
            })}
          </div>
        </div>
      </div>
    </Accordion>
  );
}

function ResourceBox({ label, max, color, icon, total, atual, onPip, onTotal, cap }) {
  return (
    <div className="panel-2" style={{ borderRadius: 9, border: '1px solid var(--line-2)', padding: '11px 12px', background: 'var(--panel-2)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 9 }}>
        <Icon name={icon} size={14} stroke={color} />
        <span className="micro" style={{ color }}>{label}</span>
        {max && <span className="mono" style={{ fontSize: 9, color: 'var(--ink-4)', marginLeft: 'auto' }}>MÁX {max}</span>}
      </div>
      <PipRow total={total} filled={atual} color={color} onToggle={onPip} size={17} />
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 11,
        paddingTop: 9, borderTop: '1px solid var(--line)' }}>
        <span className="mono" style={{ fontSize: 9.5, color: 'var(--ink-3)', letterSpacing: '0.1em' }}>TOTAL</span>
        <Counter value={total} set={onTotal} min={1} max={cap} accent={color} />
      </div>
    </div>
  );
}

/* ---- 04 Proficiências & Defesa ---- */
function ProficienciasPanel() {
  const { char } = useGame();
  const c = char.combate;
  const fmt = (a) => (char.attrs[a] >= 0 ? '+' : '') + char.attrs[a];
  const skillBonus = (s) => {
    const b = char.attrs[s.attr] + (s.prof ? char.prof : 0);
    return (b >= 0 ? '+' : '') + b;
  };
  return (
    <Accordion idx="04" title="Proficiências & Defesa"
      summary="Defesa · Perícias · Deslocamento">
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 9, paddingTop: 13 }}>
        <StatTile label="Red. de Dano" value={c.reducao} accent="var(--ink)" />
        <StatTile label="Prof." value={'+' + char.prof} accent="var(--arc)" />
        <StatTile label="Iniciativa" value={(c.iniciativa >= 0 ? '+' : '') + c.iniciativa} accent="var(--ink)" />
        <StatTile label="Tamanho" value={c.tamanho} accent="var(--ink-2)" sub="" />
      </div>
      <div style={{ marginTop: 9, background: 'var(--panel-3)', borderRadius: 7, border: '1px solid var(--line)',
        padding: '9px 12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span className="micro">Deslocamento</span>
        <span className="mono" style={{ fontSize: 13, color: 'var(--ink)' }}>{c.desloc}</span>
      </div>

      <div style={{ marginTop: 16, marginBottom: 9 }}>
        <SectionLabel idx="//" name="Perícias" />
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {char.skills.map(s => (
          <div key={s.nome} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 4px',
            borderBottom: '1px solid var(--line)' }}>
            <span style={{ width: 9, height: 9, borderRadius: '50%', flexShrink: 0,
              border: `1.5px solid ${s.prof ? 'var(--arc)' : 'var(--line-3)'}`,
              background: s.prof ? 'var(--arc)' : 'transparent',
              boxShadow: s.prof ? '0 0 7px -1px var(--arc)' : 'none' }} />
            <span style={{ flex: 1, fontSize: 13.5, color: s.prof ? 'var(--ink)' : 'var(--ink-2)' }}>{s.nome}</span>
            <span className="mono" style={{ fontSize: 10, color: 'var(--ink-4)', width: 30 }}>{s.attr}</span>
            <span className="mono" style={{ fontSize: 14, fontWeight: 600, color: s.prof ? 'var(--arc)' : 'var(--ink-3)', width: 30, textAlign: 'right' }}>
              {skillBonus(s)}
            </span>
          </div>
        ))}
      </div>
    </Accordion>
  );
}

function FichaScreen() {
  return (
    <div className="screen-pad">
      <IdentityHeader />
      <OrigemPanel />
      <AtributosPanel />
      <StatusVitalPanel />
      <ProficienciasPanel />
    </div>
  );
}

window.FichaScreen = FichaScreen;
})();
