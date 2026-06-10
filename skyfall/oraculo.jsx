/* ============================================================
   oraculo.jsx — Chatbot "Oráculo de Opath" (RAG simulado)
   ============================================================ */
(function () {
const { useState, useRef, useEffect } = React;
const { useGame, Icon, Sigil } = window;

/* scripted knowledge base — keyword -> {answer, fonte} */
const KB = [
  { keys: ['engenhoca', 'magitec', 'engenhocas'],
    answer: 'Engenhocas Magitec são dispositivos que canalizam Aetherium por meio de Fragmentos Arcanos. Cada engenhoca tem um valor de FRAG que conta para o seu Limite de Fragmentação Arcana (CAR + Proficiência × 2). Ao ativar uma engenhoca, gaste os Fragmentos indicados; se o limite for excedido, ela falha e gera 1 Ponto de Sombra.',
    fonte: 'Cap. 7 — Tecnologia Arcana · "Do Aetherium às Engenhocas"' },
  { keys: ['sombra', 'corrup'],
    answer: 'Pontos de Sombra representam a corrupção arcana acumulada. Você ganha Sombra ao forçar conjurações, falhar com engenhocas instáveis ou tocar relíquias proibidas. Ao encher a trilha, a personagem sofre uma Marca de Sombra — uma transformação narrativa permanente conforme decisão do Mestre.',
    fonte: 'Cap. 4 — Magia · "O Preço do Poder"' },
  { keys: ['catarse', 'melancolia'],
    answer: 'A Melancolia da personagem concede Pontos de Catarse (máximo 5). Gaste 1 Catarse para transformar uma falha em sucesso parcial, ou para invocar uma cena de flashback que altere a narrativa. Catarse recarrega quando você interpreta sua Melancolia em momentos de peso emocional.',
    fonte: 'Cap. 2 — Traços Trágicos · "Catarse e Melancolia"' },
  { keys: ['fragment', 'arcano', 'arcanos'],
    answer: 'O Limite de Fragmentação Arcana é calculado por CAR + (Proficiência × 2). Ele define quantos Fragmentos Arcanos em itens mágicos e engenhocas você pode portar ativos ao mesmo tempo. Exceder o limite causa instabilidade arcana.',
    fonte: 'Cap. 7 — Tecnologia Arcana · "Limites de Carga Arcana"' },
  { keys: ['proteç', 'protecao', 'defesa', 'cd'],
    answer: 'A Proteção de um atributo é a dificuldade para resistir a efeitos direcionados a ele: 10 + Atributo + Bônus de Proficiência. Por exemplo, uma magia que ataca a CON do alvo deve superar a Proteção de CON dele.',
    fonte: 'Cap. 3 — Atributos · "Proteções"' },
  { keys: ['morte', 'morrer', 'inconsciente'],
    answer: 'Ao chegar a 0 PV, role Testes de Morte (1d20): 10 ou mais é sucesso, abaixo é falha. Três sucessos estabilizam; três falhas significam a morte. Um 20 natural recupera 1 PV; um 1 natural conta como duas falhas.',
    fonte: 'Cap. 5 — Combate · "À Beira do Véu"' },
  { keys: ['camada', 'superficial', 'rasa', 'profunda', 'magia'],
    answer: 'As magias se dividem em três camadas de profundidade arcana: Superficial (baixo custo de Ênfase, efeitos imediatos), Rasa (custo médio, efeitos de cena) e Profunda (alto custo e risco de Sombra, efeitos poderosos). Quanto mais profunda a camada, maior o custo em Ênfase.',
    fonte: 'Cap. 4 — Magia · "As Três Camadas"' },
  { keys: ['ênfase', 'enfase'],
    answer: 'Ênfase é o recurso gasto para conjurar magias e ativar habilidades em cena. Você recupera toda a Ênfase em um descanso. O custo de cada magia depende da sua camada (Superficial, Rasa ou Profunda).',
    fonte: 'Cap. 4 — Magia · "Conjuração e Ênfase"' },
  { keys: ['vantagem', 'desvantagem'],
    answer: 'Com Vantagem, role 2d20 e use o maior resultado; com Desvantagem, use o menor. Elas não se acumulam: múltiplas fontes ainda resultam em apenas um dado extra.',
    fonte: 'Cap. 1 — Mecânica Central · "O Teste de d20"' },
  { keys: ['legado', 'humani', 'anuro', 'elfe'],
    answer: 'O Legado descreve a origem ancestral e cultural da personagem (Humani, Anuro, Elfe e outros povos de Opath). Cada Legado concede traços narrativos e poderes próprios, muitos ligados à Herança e ao Antecedente escolhidos.',
    fonte: 'Cap. 2 — Origem · "Os Povos de Opath"' },
];

const SUGGEST = ['Como funcionam as Engenhocas Magitec?', 'O que são Pontos de Sombra?', 'Como uso a Catarse?', 'Como funcionam os Testes de Morte?'];

function findAnswer(q) {
  const t = q.toLowerCase();
  const hit = KB.find(e => e.keys.some(k => t.includes(k)));
  if (hit) return hit;
  return { answer: 'Não encontrei essa regra específica nos trechos vetorizados do livro de Skyfall. Tente reformular ou pergunte sobre Engenhocas Magitec, Sombra, Catarse, Ênfase, Proteções, Testes de Morte ou as Camadas de magia.', fonte: null };
}

function OraculoScreen() {
  const [msgs, setMsgs] = useState([
    { who: 'bot', text: 'Saudações, viajante de Opath. Sou o Oráculo — consulto o livro oficial de Skyfall para tirar suas dúvidas de regras sem pausar a sessão. O que deseja saber?', fonte: null },
  ]);
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [msgs, typing]);

  const send = (text) => {
    const q = (text ?? input).trim();
    if (!q || typing) return;
    setMsgs(m => [...m, { who: 'me', text: q }]);
    setInput('');
    setTyping(true);
    setTimeout(() => {
      const a = findAnswer(q);
      setTyping(false);
      setMsgs(m => [...m, { who: 'bot', text: a.answer, fonte: a.fonte }]);
    }, 850 + Math.random() * 500);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* oracle banner */}
      <div style={{ flex: '0 0 auto', display: 'flex', alignItems: 'center', gap: 11, padding: '11px 15px',
        borderBottom: '1px solid var(--line-2)', background: 'rgba(8,17,18,0.6)' }}>
        <Sigil size={30} />
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 14, color: 'var(--ink)' }}>Oráculo de Opath</div>
          <div className="mono" style={{ fontSize: 9.5, color: 'var(--arc)', letterSpacing: '0.1em', display: 'flex', alignItems: 'center', gap: 5 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--arc)', boxShadow: '0 0 7px var(--arc)' }} />
            RAG · LIVRO OFICIAL VETORIZADO
          </div>
        </div>
      </div>

      {/* messages */}
      <div ref={scrollRef} className="screen" style={{ flex: 1, padding: '16px 14px' }}>
        {msgs.map((m, i) => <Bubble key={i} m={m} />)}
        {typing && (
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', margin: '4px 0 0 4px' }}>
            <div style={{ display: 'flex', gap: 4, padding: '11px 14px', background: 'var(--panel)',
              border: '1px solid var(--line)', borderRadius: '4px 12px 12px 12px' }}>
              {[0, 1, 2].map(n => (
                <span key={n} style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--arc)',
                  animation: `glowpulse 1s ${n * 0.18}s infinite`, opacity: 0.7 }} />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* suggestions */}
      {msgs.length <= 1 && (
        <div style={{ flex: '0 0 auto', display: 'flex', gap: 7, padding: '0 14px 10px', flexWrap: 'wrap' }}>
          {SUGGEST.map(s => (
            <button key={s} className="tap" onClick={() => send(s)}
              style={{ fontSize: 11.5, color: 'var(--arc-soft)', border: '1px solid var(--line-2)', borderRadius: 999,
                padding: '7px 12px', background: 'rgba(52,227,224,0.05)' }}>{s}</button>
          ))}
        </div>
      )}

      {/* composer */}
      <div style={{ flex: '0 0 auto', display: 'flex', gap: 9, padding: '11px 14px',
        borderTop: '1px solid var(--line-2)', background: 'rgba(8,17,18,0.6)' }}>
        <input value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') send(); }}
          placeholder="Dúvida rápida de regra…"
          style={{ flex: 1, background: 'var(--panel-3)', border: '1px solid var(--line-2)', borderRadius: 999,
            padding: '11px 16px', color: 'var(--ink)', fontSize: 13.5, outline: 'none' }}
          onFocus={e => e.target.style.borderColor = 'var(--line-3)'}
          onBlur={e => e.target.style.borderColor = 'var(--line-2)'} />
        <button className="tap" onClick={() => send()}
          style={{ width: 44, height: 44, borderRadius: '50%', background: 'var(--arc)', flexShrink: 0,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 18px -4px var(--arc-glow)' }}>
          <Icon name="send" size={19} stroke="var(--void)" />
        </button>
      </div>
    </div>
  );
}

function Bubble({ m }) {
  const me = m.who === 'me';
  return (
    <div style={{ display: 'flex', justifyContent: me ? 'flex-end' : 'flex-start', marginBottom: 12 }}>
      <div style={{ maxWidth: '82%' }}>
        <div style={{ padding: '11px 14px', fontSize: 13.5, lineHeight: 1.55,
          color: me ? 'var(--void)' : 'var(--ink)',
          background: me ? 'var(--arc)' : 'var(--panel)',
          border: me ? 'none' : '1px solid var(--line)',
          borderRadius: me ? '12px 12px 4px 12px' : '4px 12px 12px 12px',
          boxShadow: me ? '0 0 18px -8px var(--arc-glow)' : 'none' }}>
          {m.text}
        </div>
        {m.fonte && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, margin: '7px 0 0 4px' }}>
            <Icon name="ficha" size={12} stroke="var(--ink-4)" />
            <span className="mono" style={{ fontSize: 9.5, color: 'var(--ink-4)', letterSpacing: '0.04em' }}>{m.fonte}</span>
          </div>
        )}
      </div>
    </div>
  );
}

window.OraculoScreen = OraculoScreen;
})();
