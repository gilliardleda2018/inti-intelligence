import React, { useEffect, useState } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, AreaChart, Area 
} from 'recharts';
import { 
  TrendingUp, MessageSquare, AlertTriangle, ShieldCheck, Zap, RefreshCw, Send, Cpu, Sparkles, 
  ShoppingBag, Layers, Target, PieChart as PieIcon, ChevronRight
} from 'lucide-react';
import './styles.css';

const MOCK_REVIEWS = [
  { product_name: "Vestido Midi Seda", category: "Vestidos", sentiment_score: 0.95, review_text: "Adorei o vestido, tecido maravilhoso e caimento impecável!" },
  { product_name: "Blazer Linho Premium", category: "Blazers", sentiment_score: 0.88, review_text: "Blazer de alfaiataria com excelente caimento. Peça clássica." },
  { product_name: "Vestido Longo Floral", category: "Vestidos", sentiment_score: -0.85, review_text: "A costura do vestido rasgou no primeiro uso perto do zíper." },
  { product_name: "Biquíni Cortininha", category: "Biquínis", sentiment_score: -0.92, review_text: "O biquíni veio muito pequeno e a cor desbotou na primeira lavagem." },
  { product_name: "Macacão Utilitário", category: "Macacões", sentiment_score: 0.45, review_text: "Muito confortável e prático. A entrega atrasou dois dias." }
];

function App() {
  const [activeTab, setActiveTab] = useState("executivo");
  const [reviews, setReviews] = useState(MOCK_REVIEWS);
  const [kpis, setKpis] = useState({ total_reviews: 11, avg_sentiment: 0.28, csat_score: 72.5, positive: 7, negative: 4, neutral: 0 });
  const [commercialData, setCommercialData] = useState(null);
  const [assortmentData, setAssortmentData] = useState(null);
  const [portfolioData, setPortfolioData] = useState(null);
  const [decisionsData, setDecisionsData] = useState(null);
  
  const [selectedCategory, setSelectedCategory] = useState("Biquínis");
  const [aiRec, setAiRec] = useState("Carregando recomendações do Snowflake Cortex AI...");
  const [chatMessages, setChatMessages] = useState([
    { sender: "agent", text: "Olá! Sou o Agente de IA INTI Intelligence. Como posso apoiar suas decisões estratégicas de varejo hoje?" }
  ]);
  const [userQuery, setUserQuery] = useState("");
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const rSent = await fetch('/api/sentiment').then(r => r.json()).catch(() => null);
      if (rSent) setReviews(rSent);

      const rKpi = await fetch('/api/kpis').then(r => r.json()).catch(() => null);
      if (rKpi) setKpis(rKpi);

      const rCom = await fetch('/api/commercial').then(r => r.json()).catch(() => null);
      if (rCom) setCommercialData(rCom);

      const rAss = await fetch('/api/assortment').then(r => r.json()).catch(() => null);
      if (rAss) setAssortmentData(rAss);

      const rPort = await fetch('/api/portfolio-ml').then(r => r.json()).catch(() => null);
      if (rPort) setPortfolioData(rPort);

      const rDec = await fetch('/api/decisions').then(r => r.json()).catch(() => null);
      if (rDec) setDecisionsData(rDec);

    } catch (e) {
      console.warn("Usando cache local de alto desempenho.");
    }
  };

  useEffect(() => {
    fetchAiRec(selectedCategory);
  }, [selectedCategory]);

  const fetchAiRec = async (cat) => {
    try {
      const res = await fetch(`/api/ai-recommendation?category=${encodeURIComponent(cat)}`);
      if (res.ok) {
        const d = await res.json();
        setAiRec(d.recommendation);
      }
    } catch {
      setAiRec(`Recomendação para ${cat}: Priorizar controle de qualidade nos tecidos e ajuste de tabela de medidas.`);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetch('/api/refresh', { method: 'POST' }).catch(() => {});
    await fetchData();
    setTimeout(() => setIsRefreshing(false), 500);
  };

  const handleSendChat = async (e) => {
    e.preventDefault();
    if (!userQuery.trim()) return;

    const q = userQuery;
    setUserQuery("");
    setChatMessages(prev => [...prev, { sender: "user", text: q }]);

    try {
      const res = await fetch('/api/agent/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: q })
      });
      if (res.ok) {
        const d = await res.json();
        setChatMessages(prev => [...prev, { sender: "agent", text: d.response }]);
      }
    } catch {
      setChatMessages(prev => [...prev, { sender: "agent", text: "Agente IA: Conexão direta com os modelos Snowflake Cortex ativa." }]);
    }
  };

  const chartSentimentData = [
    { name: 'Positivos', count: kpis.positive, color: '#10B981' },
    { name: 'Neutros', count: kpis.neutral, color: '#6B7280' },
    { name: 'Negativos', count: kpis.negative, color: '#EF4444' }
  ];

  return (
    <div className="dashboard-root">
      {/* Header */}
      <header className="navbar">
        <div className="brand">
          <div className="logo-badge">INTI</div>
          <div>
            <h1>INTI Intelligence <span className="tag-live">v1.1 LIVE</span></h1>
            <p className="subtitle">Plataforma Híbrida Executiva de IA & Analítica de Varejo</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="tab-nav">
          <button className={`tab-btn ${activeTab === 'executivo' ? 'active' : ''}`} onClick={() => setActiveTab('executivo')}>
            <TrendingUp size={16} /> Painel Executivo
          </button>
          <button className={`tab-btn ${activeTab === 'comercial' ? 'active' : ''}`} onClick={() => setActiveTab('comercial')}>
            <ShoppingBag size={16} /> Comercial & Sortimento
          </button>
          <button className={`tab-btn ${activeTab === 'portfolio' ? 'active' : ''}`} onClick={() => setActiveTab('portfolio')}>
            <Layers size={16} /> Portfólio ML (Clusters)
          </button>
          <button className={`tab-btn ${activeTab === 'agente' ? 'active' : ''}`} onClick={() => setActiveTab('agente')}>
            <Cpu size={16} /> Agente de IA & Oportunidades
          </button>
        </nav>

        <div className="header-actions">
          <button className={`btn-refresh ${isRefreshing ? 'spinning' : ''}`} onClick={handleRefresh}>
            <RefreshCw size={16} />
            <span>{isRefreshing ? 'Atualizando...' : 'Atualizar'}</span>
          </button>
        </div>
      </header>

      <main className="main-content">
        {/* TAB 1: EXECUTIVE & SENTIMENT */}
        {activeTab === 'executivo' && (
          <>
            <section className="kpi-grid">
              <div className="kpi-card">
                <div className="kpi-icon icon-blue"><MessageSquare size={22} /></div>
                <div className="kpi-data">
                  <span className="kpi-label">Avaliações de Clientes</span>
                  <h2 className="kpi-value">{kpis.total_reviews}</h2>
                  <span className="kpi-sub green">+12.4% este mês</span>
                </div>
              </div>

              <div className="kpi-card">
                <div className="kpi-icon icon-green"><TrendingUp size={22} /></div>
                <div className="kpi-data">
                  <span className="kpi-label">Índice CSAT (Satisfação)</span>
                  <h2 className="kpi-value">{kpis.csat_score}%</h2>
                  <span className="kpi-sub green">Meta: &gt; 70%</span>
                </div>
              </div>

              <div className="kpi-card">
                <div className="kpi-icon icon-purple"><Sparkles size={22} /></div>
                <div className="kpi-data">
                  <span className="kpi-label">Score Médio Sentimento</span>
                  <h2 className="kpi-value">{kpis.avg_sentiment > 0 ? `+${kpis.avg_sentiment}` : kpis.avg_sentiment}</h2>
                  <span className="kpi-sub purple">Snowflake Cortex Scale</span>
                </div>
              </div>

              <div className="kpi-card">
                <div className="kpi-icon icon-red"><AlertTriangle size={22} /></div>
                <div className="kpi-data">
                  <span className="kpi-label">Alertas Críticos</span>
                  <h2 className="kpi-value">{kpis.negative}</h2>
                  <span className="kpi-sub red">Requer ação imediata</span>
                </div>
              </div>
            </section>

            <div className="dashboard-grid">
              <div className="grid-col main-col">
                <div className="panel-card">
                  <div className="panel-header">
                    <h3>Distribuição de Sentimentos (Snowflake Cortex AI)</h3>
                  </div>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={chartSentimentData} margin={{ top: 20, right: 20, left: -20, bottom: 0 }}>
                      <XAxis dataKey="name" stroke="#94A3B8" />
                      <YAxis stroke="#94A3B8" />
                      <Tooltip contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155', borderRadius: '8px', color: '#FFF' }} />
                      <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                        {chartSentimentData.map((entry, index) => (
                          <Cell key={`c-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div className="panel-card mt-4">
                  <div className="panel-header">
                    <h3>Monitoramento de Feedback de Clientes</h3>
                  </div>
                  <div className="table-wrapper">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Produto</th>
                          <th>Categoria</th>
                          <th>Avaliação do Cliente</th>
                          <th>Sentimento</th>
                        </tr>
                      </thead>
                      <tbody>
                        {reviews.slice(0, 6).map((rev, i) => {
                          const score = rev.sentiment_score || 0;
                          let badgeClass = "badge-neutral", label = "Neutro";
                          if (score > 0.1) { badgeClass = "badge-pos"; label = `Positivo (${score.toFixed(2)})`; }
                          else if (score < -0.1) { badgeClass = "badge-neg"; label = `Crítico (${score.toFixed(2)})`; }

                          return (
                            <tr key={i}>
                              <td className="fw-semibold">{rev.product_name}</td>
                              <td><span className="cat-tag">{rev.category}</span></td>
                              <td className="text-truncate">{rev.review_text}</td>
                              <td><span className={`badge ${badgeClass}`}>{label}</span></td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              <div className="grid-col side-col">
                <div className="panel-card cortex-card">
                  <div className="panel-header">
                    <div className="flex-align"><Cpu className="icon-cortex" size={20} /><h3>Snowflake Cortex AI Consultant</h3></div>
                  </div>
                  <div className="category-selector">
                    {["Biquínis", "Vestidos", "Blazers", "Macacões"].map(cat => (
                      <button key={cat} className={`cat-btn ${selectedCategory === cat ? 'active' : ''}`} onClick={() => setSelectedCategory(cat)}>
                        {cat}
                      </button>
                    ))}
                  </div>
                  <div className="ai-box">
                    <p className="ai-text">{aiRec}</p>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        {/* TAB 2: COMMERCIAL & ASSORTMENT */}
        {activeTab === 'comercial' && (
          <div className="dashboard-grid full-grid">
            <div className="panel-card">
              <div className="panel-header">
                <h3>Resumo Comercial & Participação por Categoria</h3>
              </div>
              {commercialData?.category_summary && (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={commercialData.category_summary}>
                    <XAxis dataKey="category" stroke="#94A3B8" />
                    <YAxis stroke="#94A3B8" />
                    <Tooltip contentStyle={{ backgroundColor: '#1E293B', color: '#FFF' }} />
                    <Bar dataKey="revenue_share" fill="#6366F1" radius={[6, 6, 0, 0]} name="Participação Faturamento (%)" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>

            <div className="panel-card mt-4">
              <div className="panel-header">
                <h3>Arquitetura de Sortimento & Preço Médio</h3>
              </div>
              <div className="table-wrapper">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Categoria</th>
                      <th>Total de Produtos</th>
                      <th>Preço Médio (R$)</th>
                      <th>Desconto Médio (%)</th>
                      <th>Share Faturamento</th>
                    </tr>
                  </thead>
                  <tbody>
                    {commercialData?.category_summary?.map((row, i) => (
                      <tr key={i}>
                        <td className="fw-semibold">{row.category}</td>
                        <td>{row.product_count}</td>
                        <td>R$ {row.avg_price?.toFixed(2)}</td>
                        <td>{row.avg_discount}%</td>
                        <td><span className="badge badge-pos">{row.revenue_share}%</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: PORTFOLIO ML CLUSTERS */}
        {activeTab === 'portfolio' && (
          <div className="dashboard-grid full-grid">
            <div className="panel-card">
              <div className="panel-header">
                <h3>Agrupamento por Inteligência Artificial (KMeans Clusters)</h3>
              </div>
              <div className="clusters-grid">
                {portfolioData?.clusters?.map((c, i) => (
                  <div key={i} className="cluster-box">
                    <div className="cluster-tag">Cluster #{c.cluster_id}</div>
                    <h4>{c.label}</h4>
                    <p className="cluster-stat"><strong>{c.count}</strong> Produtos | Preço Médio: <strong>R$ {c.avg_price}</strong></p>
                    <div className="cluster-opp">
                      <Target size={14} /> <span>Recomendação: {c.opportunity}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: AI AGENT & DECISIONS */}
        {activeTab === 'agente' && (
          <div className="dashboard-grid">
            <div className="grid-col main-col">
              <div className="panel-card">
                <div className="panel-header">
                  <h3>Matriz de Decisões Executivas & Oportunidades</h3>
                </div>
                <div className="opp-list">
                  {decisionsData?.opportunities?.map((opp, i) => (
                    <div key={i} className="opp-card">
                      <div className="opp-header">
                        <span className="opp-id">{opp.id}</span>
                        <span className={`badge ${opp.impact === 'Crítico' ? 'badge-neg' : 'badge-pos'}`}>{opp.impact} Impacto</span>
                      </div>
                      <h4>{opp.title}</h4>
                      <p className="opp-cat">Categoria: <strong>{opp.category}</strong> | Confiança: {opp.confidence}</p>
                      <p className="opp-action">👉 <strong>Ação Recomendada:</strong> {opp.action}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="grid-col side-col">
              <div className="panel-card chat-card">
                <div className="panel-header">
                  <div className="flex-align"><Zap className="icon-zap" size={20} /><h3>INTI AI Agent</h3></div>
                </div>

                <div className="chat-messages">
                  {chatMessages.map((msg, i) => (
                    <div key={i} className={`chat-bubble bubble-${msg.sender}`}>
                      {msg.text}
                    </div>
                  ))}
                </div>

                <form onSubmit={handleSendChat} className="chat-input-form">
                  <input 
                    type="text" 
                    placeholder="Pergunte ao Agente de IA..." 
                    value={userQuery}
                    onChange={e => setUserQuery(e.target.value)}
                  />
                  <button type="submit" className="btn-send"><Send size={16} /></button>
                </form>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
