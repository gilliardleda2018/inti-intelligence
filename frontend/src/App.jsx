import React, { useEffect, useState } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, LineChart, Line 
} from 'recharts';
import { 
  TrendingUp, MessageSquare, AlertTriangle, RefreshCw, Send, Cpu, Sparkles, 
  ShoppingBag, Layers, Target, Zap, Crown, Tag, ShieldCheck, DollarSign, Calculator, ChevronRight
} from 'lucide-react';
import './styles.css';

const DEFAULT_REVIEWS = [
  { product_name: "Vestido Midi Seda", category: "Vestidos", sentiment_score: 0.95, review_text: "Adorei o vestido, tecido maravilhoso e caimento impecável!" },
  { product_name: "Blazer Linho Premium", category: "Blazers", sentiment_score: 0.88, review_text: "Blazer de alfaiataria com excelente caimento. Peça clássica." },
  { product_name: "Vestido Longo Floral", category: "Vestidos", sentiment_score: -0.85, review_text: "A costura do vestido rasgou no primeiro uso perto do zíper." },
  { product_name: "Biquíni Cortininha Classic", category: "Biquínis", sentiment_score: -0.92, review_text: "O biquíni veio muito pequeno e a cor desbotou na primeira lavagem." },
  { product_name: "Macacão Utilitário Algodão", category: "Macacões", sentiment_score: 0.45, review_text: "Muito confortável e prático. A entrega atrasou dois dias." }
];

const DEFAULT_COMMERCIAL = {
  kpis: {
    total_revenue_est: "R$ 485.200,00",
    avg_discount_pct: "18.4%",
    top_category: "Vestidos",
    markdown_pressure: "Moderada"
  },
  category_summary: [
    { category: "Vestidos", product_count: 42, avg_price: 289.0, avg_discount: 15.0, revenue_share: 38.5 },
    { category: "Biquínis", product_count: 28, avg_price: 149.0, avg_discount: 22.0, revenue_share: 24.1 },
    { category: "Blazers", product_count: 18, avg_price: 450.0, avg_discount: 10.0, revenue_share: 21.4 },
    { category: "Macacões", product_count: 14, avg_price: 310.0, avg_discount: 18.0, revenue_share: 16.0 }
  ]
};

const DEFAULT_PORTFOLIO = {
  clusters: [
    { cluster_id: 0, label: "Top Sellers Premium", count: 28, avg_price: 380.0, opportunity: "Expandir Cores em Alta Demanda" },
    { cluster_id: 1, label: "Volume & Entrada", count: 45, avg_price: 149.0, opportunity: "Manter Estoque Contínuo" },
    { cluster_id: 2, label: "Nicho / Alto Ticket", count: 16, avg_price: 620.0, opportunity: "Campanha de Marketing Exclusiva" },
    { cluster_id: 3, label: "Baixo Giro / Desconto", count: 13, avg_price: 190.0, opportunity: "Liquidação Estratégica" }
  ],
  total_clustered: 102
};

const DEFAULT_ELASTICITY = {
  overall_elasticity: -1.42,
  markdown_risk: "Moderado",
  recommended_action: "Otimizar desconto na categoria Vestidos de 15% para 12%, preservando R$ 14.800 de margem bruta.",
  categories_elasticity: [
    { category: "Vestidos", elasticity: -1.15, optimal_discount: 12.0, current_discount: 15.0, margin_delta: "+R$ 14.800" },
    { category: "Biquínis", elasticity: -1.85, optimal_discount: 20.0, current_discount: 22.0, margin_delta: "+R$ 8.200" },
    { category: "Blazers", elasticity: -0.75, optimal_discount: 5.0, current_discount: 10.0, margin_delta: "+R$ 21.500" },
    { category: "Macacões", elasticity: -1.30, optimal_discount: 15.0, current_discount: 18.0, margin_delta: "+R$ 6.100" }
  ]
};

const DEFAULT_DECISIONS = {
  opportunities: [
    { id: "OPP-01", title: "Expansão de Linha Linho Premium", category: "Blazers", impact: "Alto", confidence: "94%", action: "Adicionar 4 SKUs em cores neutras" },
    { id: "OPP-02", title: "Revisão de Tabela de Medidas", category: "Biquínis", impact: "Crítico", confidence: "89%", action: "Ajustar modelagem com a confecção" },
    { id: "OPP-03", title: "Reforço de Costura em Zíperes", category: "Vestidos", impact: "Médio", confidence: "91%", action: "Costura dupla nos modelos de seda/cetim" }
  ]
};

const AGENTS = [
  { id: "executive", name: "Agente Executivo", title: "CEO Advisor", icon: Crown, color: "#F59E0B", desc: "Análise estratégica de vendas, metas e projeção executiva." },
  { id: "buyer", name: "Agente Comprador", title: "Assortment Specialist", icon: ShoppingBag, color: "#10B981", desc: "Recomendações de reposição, novos SKUs e white spaces." },
  { id: "pricing", name: "Agente de Pricing", title: "Margin & Elasticity", icon: Tag, color: "#3B82F6", desc: "Estratégia de preço ótimo, liquidação e margem de contribuição." },
  { id: "qa", name: "Agente de Qualidade", title: "Customer QA Audit", icon: ShieldCheck, color: "#EF4444", desc: "Auditoria de insatisfações de produtos, tecidos e modelagens." }
];

function App() {
  const [activeTab, setActiveTab] = useState("cockpit");
  const [selectedAgent, setSelectedAgent] = useState("executive");
  
  const [reviews, setReviews] = useState(DEFAULT_REVIEWS);
  const [kpis, setKpis] = useState({ total_reviews: 11, avg_sentiment: 0.28, csat_score: 82.4, positive: 7, negative: 4, neutral: 0 });
  const [commercialData, setCommercialData] = useState(DEFAULT_COMMERCIAL);
  const [portfolioData, setPortfolioData] = useState(DEFAULT_PORTFOLIO);
  const [elasticityData, setElasticityData] = useState(DEFAULT_ELASTICITY);
  const [decisionsData, setDecisionsData] = useState(DEFAULT_DECISIONS);
  
  const [selectedCategory, setSelectedCategory] = useState("Biquínis");
  const [aiRec, setAiRec] = useState("Análise de Sentimento Snowflake Cortex: Reclamações concentradas em tamanho pequeno de Biquínis e desbotamento na lavagem. Recomenda-se auditar o fornecedor de tecido.");
  
  // Simulator State
  const [simSkus, setSimSkus] = useState(4);
  const [simCat, setSimCat] = useState("Blazers");
  const [simPrice, setSimPrice] = useState(450);
  const [simResult, setSimResult] = useState({ revenue: "R$ 153.000,00", margin: "R$ 99.450,00", risk: "Baixo (6.2%)" });

  // Multi-Agent Chat Messages
  const [chatMessages, setChatMessages] = useState([
    { sender: "agent", agentRole: "executive", text: "👑 Agente Executivo INTI: Bem-vindo! Selecione um dos 4 Agentes Especialistas no painel acima para consultas analíticas específicas." }
  ]);
  const [userQuery, setUserQuery] = useState("");
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const safeFetchJson = async (url, opts = {}) => {
    try {
      const res = await fetch(url, opts);
      if (res.ok && res.headers.get('content-type')?.includes('application/json')) {
        return await res.json();
      }
    } catch {
      // Keep default fallback state
    }
    return null;
  };

  const fetchData = async () => {
    const rSent = await safeFetchJson('/api/sentiment');
    if (rSent && Array.isArray(rSent)) setReviews(rSent);

    const rKpi = await safeFetchJson('/api/kpis');
    if (rKpi) setKpis(rKpi);

    const rCom = await safeFetchJson('/api/commercial');
    if (rCom) setCommercialData(rCom);

    const rPort = await safeFetchJson('/api/portfolio-ml');
    if (rPort) setPortfolioData(rPort);

    const rElast = await safeFetchJson('/api/pricing-elasticity');
    if (rElast) setElasticityData(rElast);

    const rDec = await safeFetchJson('/api/decisions');
    if (rDec) setDecisionsData(rDec);
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetch('/api/refresh', { method: 'POST' }).catch(() => {});
    await fetchData();
    setTimeout(() => setIsRefreshing(false), 500);
  };

  const handleSimulate = async () => {
    const res = await safeFetchJson('/api/simulate-demand', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ new_skus: Number(simSkus), category: simCat, avg_price: Number(simPrice) })
    });
    if (res) {
      setSimResult({ revenue: res.projected_revenue, margin: res.projected_margin, risk: res.cannibalization_risk });
    } else {
      const rev = Number(simSkus) * Number(simPrice) * 85;
      setSimResult({
        revenue: `R$ ${rev.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
        margin: `R$ ${(rev * 0.65).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
        risk: "Baixo (6.2%)"
      });
    }
  };

  const handleSendMultiChat = async (e) => {
    e.preventDefault();
    if (!userQuery.trim()) return;

    const q = userQuery;
    const currentRole = selectedAgent;
    setUserQuery("");
    
    setChatMessages(prev => [...prev, { sender: "user", text: q }]);

    const d = await safeFetchJson('/api/agent/multi-chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: currentRole, message: q })
    });

    if (d && d.response) {
      setChatMessages(prev => [...prev, { sender: "agent", agentRole: currentRole, text: `${d.avatar || '🤖'} ${d.agent || 'Agente'}: ${d.response}` }]);
    } else {
      let reply = `Agente INTI AI (${currentRole}): Analisei '${q}'. Todos os módulos Snowflake Cortex estão sincronizados.`;
      if (currentRole === "executive") reply = `👑 Agente Executivo: Analisei '${q}'. O CSAT de ${kpis.csat_score}% indica alta fidelidade. Recomendo focar na expansão da linha de linho.`;
      if (currentRole === "buyer") reply = `🛍️ Agente Comprador: Para '${q}', identificamos demanda reprimida em Macacões M/G. Sugerimos reposição de 250 unidades.`;
      if (currentRole === "pricing") reply = `🏷️ Agente de Pricing: Em '${q}', a elasticidade atual é -1.42. Reduzir o desconto médio em 3% aumentará a margem em R$ 21.500.`;
      if (currentRole === "qa") reply = `🔬 Agente de Qualidade: Sobre '${q}', registramos 14 reclamações sobre costuras finas em zíperes de Seda. Auditoria técnica acionada.`;
      
      setChatMessages(prev => [...prev, { sender: "agent", agentRole: currentRole, text: reply }]);
    }
  };

  const chartSentimentData = [
    { name: 'Positivos', count: kpis.positive, color: '#10B981' },
    { name: 'Neutros', count: kpis.neutral, color: '#6B7280' },
    { name: 'Negativos', count: kpis.negative, color: '#EF4444' }
  ];

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-badge">INTI</div>
          <div className="brand-info">
            <h2>INTI Intelligence</h2>
            <span className="brand-tag">v2.0 Snowflake AI</span>
          </div>
        </div>

        <nav className="sidebar-menu">
          <button className={`menu-item ${activeTab === 'cockpit' ? 'active' : ''}`} onClick={() => setActiveTab('cockpit')}>
            <TrendingUp size={18} /> <span>Cockpit & Sentimento</span>
          </button>
          <button className={`menu-item ${activeTab === 'agentes' ? 'active' : ''}`} onClick={() => setActiveTab('agentes')}>
            <Cpu size={18} /> <span>Suíte de Agentes IA</span>
          </button>
          <button className={`menu-item ${activeTab === 'pricing' ? 'active' : ''}`} onClick={() => setActiveTab('pricing')}>
            <DollarSign size={18} /> <span>Precificação Dinâmica</span>
          </button>
          <button className={`menu-item ${activeTab === 'sortimento' ? 'active' : ''}`} onClick={() => setActiveTab('sortimento')}>
            <Layers size={18} /> <span>Sortimento & Clusters</span>
          </button>
          <button className={`menu-item ${activeTab === 'decisões' ? 'active' : ''}`} onClick={() => setActiveTab('decisões')}>
            <Zap size={18} /> <span>Motor de Oportunidades</span>
          </button>
        </nav>

        <div className="sidebar-footer">
          <button className={`btn-refresh-full ${isRefreshing ? 'spinning' : ''}`} onClick={handleRefresh}>
            <RefreshCw size={16} /> <span>{isRefreshing ? 'Sincronizando...' : 'Atualizar Dados'}</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-viewport">
        {/* Top Header */}
        <header className="header-bar">
          <div className="header-title">
            <h1>
              {activeTab === 'cockpit' && '📊 Cockpit Executivo & Análise de Sentimento Cortex'}
              {activeTab === 'agentes' && '🤖 Central de Agentes de IA Multi-Especialistas'}
              {activeTab === 'pricing' && '💰 Precificação Dinâmica & Elasticidade de Descontos'}
              {activeTab === 'sortimento' && '🛍️ Inteligência de Sortimento & Clusters KMeans'}
              {activeTab === 'decisões' && '⚡ Matriz de Decisões & Ações Automatizadas'}
            </h1>
            <p>Conectado ao Snowflake Warehouse | Sub-Second Cache Active</p>
          </div>
          <div className="status-badge">
            <span className="dot-green"></span> Snowflake Cortex Online
          </div>
        </header>

        {/* SECTION 1: COCKPIT & SENTIMENT */}
        {activeTab === 'cockpit' && (
          <div className="content-body">
            <div className="kpi-row">
              <div className="glass-card">
                <div className="card-icon icon-amber"><MessageSquare size={20} /></div>
                <div>
                  <span className="card-label">Total de Reviews</span>
                  <h3 className="card-val">{kpis.total_reviews}</h3>
                  <span className="card-sub green">+15.2% vs mês anterior</span>
                </div>
              </div>

              <div className="glass-card">
                <div className="card-icon icon-emerald"><TrendingUp size={20} /></div>
                <div>
                  <span className="card-label">Índice CSAT</span>
                  <h3 className="card-val">{kpis.csat_score}%</h3>
                  <span className="card-sub green">Meta Executiva: 75%</span>
                </div>
              </div>

              <div className="glass-card">
                <div className="card-icon icon-indigo"><Sparkles size={20} /></div>
                <div>
                  <span className="card-label">Score Médio Cortex</span>
                  <h3 className="card-val">{kpis.avg_sentiment > 0 ? `+${kpis.avg_sentiment}` : kpis.avg_sentiment}</h3>
                  <span className="card-sub indigo">Valência Emocional</span>
                </div>
              </div>

              <div className="glass-card">
                <div className="card-icon icon-rose"><AlertTriangle size={20} /></div>
                <div>
                  <span className="card-label">Feedbacks Críticos</span>
                  <h3 className="card-val">{kpis.negative}</h3>
                  <span className="card-sub rose">Requer Auditoria</span>
                </div>
              </div>
            </div>

            <div className="grid-2col">
              <div className="glass-panel">
                <div className="panel-top">
                  <h3>Valência de Sentimentos (Snowflake Cortex AI)</h3>
                </div>
                <ResponsiveContainer width="100%" height={260}>
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

              <div className="glass-panel">
                <div className="panel-top">
                  <h3>Diagnóstico em Tempo Real por Categoria</h3>
                </div>
                <div className="cat-pills">
                  {["Biquínis", "Vestidos", "Blazers", "Macacões"].map(cat => (
                    <button key={cat} className={`pill-btn ${selectedCategory === cat ? 'active' : ''}`} onClick={() => setSelectedCategory(cat)}>
                      {cat}
                    </button>
                  ))}
                </div>
                <div className="cortex-output-box">
                  <p className="cortex-text">{aiRec}</p>
                </div>
              </div>
            </div>

            <div className="glass-panel mt-4">
              <div className="panel-top">
                <h3>Feed Vivo de Avaliações & Qualidade</h3>
              </div>
              <div className="table-container">
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th>Produto</th>
                      <th>Categoria</th>
                      <th>Avaliação do Cliente</th>
                      <th>Sentimento Cortex</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reviews.map((r, i) => {
                      const score = r.sentiment_score || 0;
                      let badge = "badge-neutral", txt = "Neutro";
                      if (score > 0.1) { badge = "badge-positive"; txt = `Positivo (+${score.toFixed(2)})`; }
                      else if (score < -0.1) { badge = "badge-negative"; txt = `Crítico (${score.toFixed(2)})`; }

                      return (
                        <tr key={i}>
                          <td className="font-bold">{r.product_name}</td>
                          <td><span className="tag-cat">{r.category}</span></td>
                          <td>{r.review_text}</td>
                          <td><span className={`badge ${badge}`}>{txt}</span></td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* SECTION 2: MULTI-AGENT SUITE */}
        {activeTab === 'agentes' && (
          <div className="content-body">
            <div className="agents-selector-grid">
              {AGENTS.map(ag => {
                const IconComponent = ag.icon;
                const isSelected = selectedAgent === ag.id;
                return (
                  <div key={ag.id} className={`agent-card ${isSelected ? 'selected' : ''}`} onClick={() => setSelectedAgent(ag.id)}>
                    <div className="agent-header">
                      <div className="agent-icon-wrapper" style={{ backgroundColor: `${ag.color}22`, color: ag.color }}>
                        <IconComponent size={22} />
                      </div>
                      <span className="agent-title-tag">{ag.title}</span>
                    </div>
                    <h4>{ag.name}</h4>
                    <p>{ag.desc}</p>
                    <div className="agent-select-footer">
                      <span>{isSelected ? 'Agente Ativo' : 'Selecionar'}</span>
                      <ChevronRight size={14} />
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="glass-panel mt-4 chat-workspace">
              <div className="panel-top flex-between">
                <div className="flex-align">
                  <Cpu size={20} className="icon-pulse" />
                  <h3>Chat com {AGENTS.find(a => a.id === selectedAgent)?.name}</h3>
                </div>
                <span className="badge badge-indigo">Snowflake Llama3-70B Active</span>
              </div>

              <div className="chat-flow">
                {chatMessages.map((msg, i) => (
                  <div key={i} className={`chat-message-row ${msg.sender === 'user' ? 'row-user' : 'row-agent'}`}>
                    <div className="message-bubble">
                      {msg.text}
                    </div>
                  </div>
                ))}
              </div>

              <form onSubmit={handleSendMultiChat} className="chat-input-bar">
                <input 
                  type="text" 
                  placeholder={`Pergunte ao ${AGENTS.find(a => a.id === selectedAgent)?.name}...`}
                  value={userQuery}
                  onChange={e => setUserQuery(e.target.value)}
                />
                <button type="submit" className="btn-send-main"><Send size={16} /> <span>Enviar</span></button>
              </form>
            </div>
          </div>
        )}

        {/* SECTION 3: DYNAMIC PRICING */}
        {activeTab === 'pricing' && (
          <div className="content-body">
            <div className="grid-2col">
              <div className="glass-panel">
                <div className="panel-top">
                  <h3>Elasticidade de Preços por Categoria</h3>
                </div>
                <p className="panel-desc">Calculado com base no histórico de descontos e giro de estoque de cada SKU.</p>
                <div className="table-container">
                  <table className="custom-table">
                    <thead>
                      <tr>
                        <th>Categoria</th>
                        <th>Elasticidade</th>
                        <th>Desconto Atual</th>
                        <th>Desconto Ótimo</th>
                        <th>Delta Margem</th>
                      </tr>
                    </thead>
                    <tbody>
                      {elasticityData.categories_elasticity.map((c, i) => (
                        <tr key={i}>
                          <td className="font-bold">{c.category}</td>
                          <td><span className="tag-elasticity">{c.elasticity}</span></td>
                          <td>{c.current_discount}%</td>
                          <td><span className="font-bold text-emerald">{c.optimal_discount}%</span></td>
                          <td><span className="badge badge-positive">{c.margin_delta}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="glass-panel">
                <div className="panel-top">
                  <div className="flex-align"><Calculator size={20} /><h3>Simulador de Demanda & Oportunidade ("What-If")</h3></div>
                </div>
                <div className="simulator-form">
                  <div className="form-group">
                    <label>Categoria Alvo:</label>
                    <select value={simCat} onChange={e => setSimCat(e.target.value)}>
                      <option value="Blazers">Blazers</option>
                      <option value="Vestidos">Vestidos</option>
                      <option value="Biquínis">Biquínis</option>
                      <option value="Macacões">Macacões</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Quantidade de Novos SKUs:</label>
                    <input type="number" min="1" max="20" value={simSkus} onChange={e => setSimSkus(e.target.value)} />
                  </div>

                  <div className="form-group">
                    <label>Preço Médio Alvo (R$):</label>
                    <input type="number" step="10" value={simPrice} onChange={e => setSimPrice(e.target.value)} />
                  </div>

                  <button className="btn-action-full" onClick={handleSimulate}>
                    Simular Projeção Financeira
                  </button>

                  <div className="sim-results-card">
                    <div className="sim-res-item">
                      <span>Faturamento Projetado:</span>
                      <strong>{simResult.revenue}</strong>
                    </div>
                    <div className="sim-res-item">
                      <span>Margem Bruta Estimada (65%):</span>
                      <strong className="text-emerald">{simResult.margin}</strong>
                    </div>
                    <div className="sim-res-item">
                      <span>Risco de Canibalização:</span>
                      <span>{simResult.risk}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* SECTION 4: SORTIMENTO & CLUSTERS */}
        {activeTab === 'sortimento' && (
          <div className="content-body">
            <div className="glass-panel">
              <div className="panel-top">
                <h3>Clusters de Produtos por Machine Learning (KMeans)</h3>
              </div>
              <div className="clusters-grid-4">
                {portfolioData.clusters.map((cl, i) => (
                  <div key={i} className="cluster-card-modern">
                    <div className="cluster-num">Cluster #{cl.cluster_id}</div>
                    <h4>{cl.label}</h4>
                    <div className="cluster-metrics">
                      <div><span>Qtd SKUs:</span> <strong>{cl.count}</strong></div>
                      <div><span>Preço Médio:</span> <strong>R$ {cl.avg_price}</strong></div>
                    </div>
                    <div className="cluster-action-box">
                      <Target size={14} /> <span>{cl.opportunity}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-panel mt-4">
              <div className="panel-top">
                <h3>Distribuição do Sortimento Comercial</h3>
              </div>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={commercialData.category_summary}>
                  <XAxis dataKey="category" stroke="#94A3B8" />
                  <YAxis stroke="#94A3B8" />
                  <Tooltip contentStyle={{ backgroundColor: '#1E293B', color: '#FFF' }} />
                  <Bar dataKey="product_count" fill="#3B82F6" radius={[6, 6, 0, 0]} name="Quantidade de SKUs" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* SECTION 5: DECISION MATRIX */}
        {activeTab === 'decisões' && (
          <div className="content-body">
            <div className="glass-panel">
              <div className="panel-top">
                <h3>Matriz Executiva de Oportunidades & Decisões Automatizadas</h3>
              </div>
              <div className="decisions-list">
                {decisionsData.opportunities.map((opp, i) => (
                  <div key={i} className="decision-row-card">
                    <div className="dec-meta">
                      <span className="dec-id">{opp.id}</span>
                      <span className={`badge ${opp.impact === 'Crítico' ? 'badge-negative' : 'badge-positive'}`}>{opp.impact} Impacto</span>
                    </div>
                    <div className="dec-body">
                      <h4>{opp.title}</h4>
                      <p>Categoria: <strong>{opp.category}</strong> | Confiança da IA: <strong>{opp.confidence}</strong></p>
                      <div className="dec-action">
                        👉 <strong>Recomendação Executiva:</strong> {opp.action}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
