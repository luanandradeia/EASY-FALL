/* ============================================================
   login.jsx — Tela de Login (Acesso Rápido)
   ============================================================ */
(function () {
const { useState } = React;
const { Sigil, Icon, Field } = window;

function LoginScreen({ onEnter }) {
  const [user, setUser] = useState('');
  const [pass, setPass] = useState('');
  const [remember, setRemember] = useState(true);
  const [busy, setBusy] = useState(false);

  const submit = (e) => {
    e && e.preventDefault();
    setBusy(true);
    setTimeout(() => { setBusy(false); onEnter(); }, 620);
  };

  return (
    <div className="screen-anim" style={{ flex: 1, display: 'flex', flexDirection: 'column',
      position: 'relative', overflow: 'hidden' }}>

      {/* drifting arcane glow */}
      <div style={{ position: 'absolute', top: '-12%', left: '50%', transform: 'translateX(-50%)',
        width: 420, height: 420, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(52,227,224,0.16), transparent 62%)',
        filter: 'blur(8px)', pointerEvents: 'none' }} />

      {/* brand block */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', padding: '40px 30px 12px', textAlign: 'center', zIndex: 1 }}>
        <div style={{ animation: 'pop .6s cubic-bezier(.2,.8,.3,1)' }}><Sigil size={66} /></div>
        <h1 className="mono" style={{ fontSize: 40, fontWeight: 700, letterSpacing: '0.16em',
          marginTop: 22, color: 'var(--ink)' }}>SKYFALL</h1>
        <div className="eyebrow" style={{ marginTop: 8 }}>Companion · Opath</div>
        <p style={{ color: 'var(--ink-3)', fontSize: 12.5, marginTop: 14, maxWidth: 250, lineHeight: 1.55 }}>
          Sua ficha, inventário e o Oráculo de regras — na palma da mão, no cenário aetherpunk de Opath.
        </p>
      </div>

      {/* form */}
      <form onSubmit={submit} style={{ padding: '8px 24px 40px', display: 'flex', flexDirection: 'column', gap: 14, zIndex: 1 }}>
        <Field label="Usuárie" placeholder="seu_acesso" value={user} onChange={setUser} />
        <div>
          <span className="micro" style={{ display: 'block', marginBottom: 5 }}>Senha</span>
          <div style={{ position: 'relative' }}>
            <input type="password" value={pass} onChange={e => setPass(e.target.value)} placeholder="••••••••"
              style={{ width: '100%', background: 'var(--panel-3)', border: '1px solid var(--line)',
                borderRadius: 7, padding: '11px 12px', color: 'var(--ink)', fontSize: 14, outline: 'none' }}
              onFocus={e => e.target.style.borderColor = 'var(--line-3)'}
              onBlur={e => e.target.style.borderColor = 'var(--line)'} />
          </div>
        </div>

        <button type="button" onClick={() => setRemember(r => !r)}
          style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '2px 0', alignSelf: 'flex-start' }}>
          <span style={{ width: 38, height: 22, borderRadius: 999, padding: 2,
            background: remember ? 'var(--arc-deep)' : 'var(--panel-3)',
            border: `1px solid ${remember ? 'var(--arc)' : 'var(--line-2)'}`,
            display: 'flex', transition: 'all .2s ease' }}>
            <span style={{ width: 16, height: 16, borderRadius: '50%', background: remember ? 'var(--arc)' : 'var(--ink-3)',
              transform: remember ? 'translateX(16px)' : 'none', transition: 'transform .2s ease',
              boxShadow: remember ? '0 0 8px var(--arc)' : 'none' }} />
          </span>
          <span className="micro" style={{ color: 'var(--ink-2)' }}>Lembrar sessão de jogo</span>
        </button>

        <button type="submit" className="btn" disabled={busy}
          style={{ marginTop: 4, opacity: busy ? 0.8 : 1, animation: busy ? 'glowpulse 1s infinite' : 'none' }}>
          {busy ? 'Sintonizando…' : <>Entrar <Icon name="bolt" size={16} stroke="var(--void)" /></>}
        </button>

        <div className="micro" style={{ textAlign: 'center', marginTop: 2, color: 'var(--ink-4)' }}>
          Autenticação segura · Sessão persistente
        </div>
      </form>
    </div>
  );
}

window.LoginScreen = LoginScreen;
})();
