/* ============================================================
   app.jsx — state store, navigation, screen routing
   ============================================================ */
const { useState: useStateA, useEffect: useEffectA, useCallback: useCallbackA } = React;
const { GameContext, Sigil, Icon, LoginScreen, FichaScreen, InventarioScreen, CenaScreen, OraculoScreen } = window;

/* ---------- seed data (mechanics seeded; identity left blank) ---------- */
const SEED = {
  identidade: { nome: '', pronomes: '', nivel: '', classe: '', jogadore: '' },
  origem: { legado: '', heranca: '', antecedente: '', maldicao: '', melancolia: '' },
  attrs: { FOR: 3, DES: 2, CON: 3, INT: 1, SAB: 2, CAR: 2 },
  attrOrder: ['FOR', 'DES', 'CON', 'INT', 'SAB', 'CAR'],
  attrNames: { FOR: 'Força', DES: 'Destreza', CON: 'Constituição', INT: 'Intelecto', SAB: 'Sabedoria', CAR: 'Carisma' },
  prof: 3,
  pv: { max: 32, atual: 32, temp: 0 },
  dadosVida: { total: 5, usados: 1 },
  catarse: { total: 3, atual: 1 },
  enfase: { total: 4, atual: 4 },
  sombra: { total: 8, atual: 0 },
  morte: { sucesso: 0, falha: 0 },
  combate: { reducao: 2, iniciativa: 2, tamanho: 'Médie', desloc: '9 m / 6 q' },
  skills: [
    { nome: 'Arcanismo', attr: 'INT', prof: true },
    { nome: 'Furtividade', attr: 'DES', prof: true },
    { nome: 'Magitec', attr: 'INT', prof: true },
    { nome: 'Atletismo', attr: 'FOR', prof: false },
    { nome: 'Intuição', attr: 'SAB', prof: true },
    { nome: 'Investigação', attr: 'INT', prof: false },
    { nome: 'Medicina', attr: 'SAB', prof: false },
    { nome: 'Persuasão', attr: 'CAR', prof: false },
    { nome: 'Intimidação', attr: 'CAR', prof: true },
    { nome: 'Percepção', attr: 'SAB', prof: false },
  ],
  riquezas: { trocados: 12, pecas: 3 },
  itens: [
    { id: 'i1', nome: 'Sabre Flexível', tipo: 'Arma', vol: 2, frag: 0, atk: 6, dano: '1d8', dtipo: 'CORTANTE',
      equipado: true, descritores: ['LEVE', 'CORTANTE', 'ACURÁCIA'], texto: 'Lâmina articulada de aço-éter. Pode ser empunhada com DES no lugar de FOR.' },
    { id: 'i2', nome: 'Pistola de Fagulha', tipo: 'Arma', vol: 1, frag: 2, atk: 5, dano: '1d6', dtipo: 'PERFURANTE',
      equipado: true, descritores: ['PERFURANTE', 'MAGITEC', 'RECARGA'], texto: 'Engenhoca magitec. Consome 1 Fragmento Arcano por disparo carregado.' },
    { id: 'i3', nome: 'Manto de Cinzas', tipo: 'Armadura', vol: 3, frag: 1, equipado: true,
      descritores: ['MÁGICO', 'LEVE'], texto: 'Concede Redução de Dano +2. Tece sombra ao redor da portadora ao anoitecer.' },
    { id: 'i4', nome: 'Sigilo de Vínculo', tipo: 'Engenhoca', vol: 1, frag: 3, equipado: false,
      descritores: ['MÁGICO', 'SIGILO'], texto: 'Armazena uma magia de camada Superficial para conjuração posterior.' },
    { id: 'i5', nome: 'Rações de Viagem', tipo: 'Consumível', vol: 2, frag: 0, equipado: false,
      descritores: ['CONSUMÍVEL'], texto: 'Suprimento para 5 dias em Opath.' },
  ],
  spells: [
    { id: 's1', nome: 'Drenar Fortitude', camada: 'Superficial', chave: 'INT', atk: 5, duracao: 'Instantânea', alcance: '9 m', custo: 0,
      efeito: 'O alvo sofre 1d8 de dano necrótico; você recupera metade em PV. Teste de Proteção de CON reduz à metade.' },
    { id: 's2', nome: 'Marcas Terríveis', camada: 'Rasa', chave: 'INT', atk: 6, duracao: '1 cena', alcance: 'Toque', custo: 1,
      efeito: 'Grava sigilos de pavor na pele do alvo. Desvantagem em testes de SAB enquanto durar a marca.' },
    { id: 's3', nome: 'Mortalha de Cinzas', camada: 'Profunda', chave: 'INT', atk: 7, duracao: '1 cena', alcance: 'Pessoal', custo: 3,
      efeito: 'Envolve-se em cinzas arcanas: Redução de Dano +4 e ataques de oportunidade contra você falham automaticamente.' },
  ],
};

/* ---------- nav config ---------- */
const NAV = [
  { id: 'ficha', icon: 'ficha', label: 'Ficha' },
  { id: 'inventario', icon: 'inv', label: 'Inventário' },
  { id: 'cena', icon: 'cena', label: 'Cena' },
  { id: 'oraculo', icon: 'oraculo', label: 'Oráculo' },
];

function BottomNav({ screen, go }) {
  return (
    <nav style={{ flex: '0 0 auto', display: 'grid', gridTemplateColumns: 'repeat(4,1fr)',
      borderTop: '1px solid var(--line-2)', background: 'rgba(6,13,14,0.92)',
      backdropFilter: 'blur(12px)', paddingBottom: 'env(safe-area-inset-bottom)' }}>
      {NAV.map(n => {
        const on = screen === n.id;
        return (
          <button key={n.id} onClick={() => go(n.id)}
            style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4,
              padding: '11px 0 12px', position: 'relative', color: on ? 'var(--arc)' : 'var(--ink-3)',
              transition: 'color .18s ease' }}>
            {on && <span style={{ position: 'absolute', top: 0, left: '28%', right: '28%', height: 2,
              background: 'var(--arc)', boxShadow: '0 0 10px var(--arc)', borderRadius: 2 }} />}
            <Icon name={n.icon} size={21} sw={on ? 1.9 : 1.5} />
            <span className="mono" style={{ fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase',
              fontWeight: on ? 600 : 400 }}>{n.label}</span>
          </button>
        );
      })}
    </nav>
  );
}

/* ---------- App ---------- */
function App() {
  const [screen, setScreen] = useStateA('login');
  const [char, setChar] = useStateA(() => {
    try { const s = localStorage.getItem('skyfall_char'); if (s) return JSON.parse(s); } catch (e) {}
    return SEED;
  });

  useEffectA(() => {
    try { localStorage.setItem('skyfall_char', JSON.stringify(char)); } catch (e) {}
  }, [char]);

  // generic patch helper: patch('pv', {atual: 5}) or patch('identidade', {nome:'x'})
  const patch = useCallbackA((key, partial) => {
    setChar(c => ({ ...c, [key]: { ...c[key], ...partial } }));
  }, []);
  const setField = useCallbackA((key, field, value) => {
    setChar(c => ({ ...c, [key]: { ...c[key], [field]: value } }));
  }, []);
  const setItems = useCallbackA((updater) => {
    setChar(c => ({ ...c, itens: typeof updater === 'function' ? updater(c.itens) : updater }));
  }, []);

  const protecao = (a) => 10 + (char.attrs[a] || 0) + char.prof;
  const cargaAtual = char.itens.reduce((s, i) => s + (i.vol || 0), 0);
  const cargaLimite = 8 + char.attrs.FOR * 2;
  const fragAtual = char.itens.reduce((s, i) => s + (i.frag || 0), 0);
  const fragLimite = char.attrs.CAR + char.prof * 2;

  const store = { char, setChar, patch, setField, setItems, protecao,
    cargaAtual, cargaLimite, fragAtual, fragLimite, go: setScreen };

  const reset = () => { setChar(SEED); };

  return (
    <GameContext.Provider value={store}>
      <div className="ambient" />
      <div className="app-shell">
        {screen === 'login'
          ? <LoginScreen onEnter={() => setScreen('ficha')} />
          : (<>
              <AppHeader screen={screen} onLogout={() => setScreen('login')} onReset={reset} />
              <div className="screen" key={screen}>
                <div className="screen-anim">
                  {screen === 'ficha' && <FichaScreen />}
                  {screen === 'inventario' && <InventarioScreen />}
                  {screen === 'cena' && <CenaScreen />}
                  {screen === 'oraculo' && <OraculoScreen />}
                </div>
              </div>
              <BottomNav screen={screen} go={setScreen} />
            </>)}
      </div>
    </GameContext.Provider>
  );
}

/* ---------- top header (inside app, not login) ---------- */
function AppHeader({ screen, onLogout }) {
  const titles = { ficha: 'Ficha de Personagem', inventario: 'Inventário', cena: 'Modo Cena', oraculo: 'Oráculo de Opath' };
  return (
    <header style={{ flex: '0 0 auto', display: 'flex', alignItems: 'center', gap: 11,
      padding: '13px 15px 12px', borderBottom: '1px solid var(--line-2)',
      background: 'rgba(6,13,14,0.85)', backdropFilter: 'blur(10px)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
        <Sigil size={26} glow={false} />
        <div>
          <div className="mono" style={{ fontSize: 9.5, letterSpacing: '0.28em', color: 'var(--arc)' }}>SKYFALL</div>
          <div style={{ fontSize: 13.5, letterSpacing: '0.04em', color: 'var(--ink)', marginTop: 1 }}>{titles[screen]}</div>
        </div>
      </div>
      <div style={{ flex: 1 }} />
      <button className="tap" onClick={onLogout}
        style={{ width: 36, height: 36, borderRadius: 8, border: '1px solid var(--line-2)',
          color: 'var(--ink-3)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Icon name="logout" size={18} />
      </button>
    </header>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
