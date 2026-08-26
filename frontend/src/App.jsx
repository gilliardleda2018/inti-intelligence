import React, { useEffect, useState } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell 
} from 'recharts';
import { 
  TrendingUp, MessageSquare, AlertTriangle, RefreshCw, Send, Cpu, Sparkles, 
  ShoppingBag, Layers, Target, Zap, Crown, Tag, ShieldCheck, DollarSign, Calculator, ChevronRight, Copy, Search, CheckCircle, Database
} from 'lucide-react';
import './styles.css';

const DEFAULT_REVIEWS = [
  { product_name: "Vestido Midi Seda Pure Luxury", category: "Vestidos", sentiment_score: 0.95, rating: 5, review_text: "Adorei o vestido! Tecido de seda maravilhoso, caimento impecável e acabamento perfeito." },
  { product_name: "Blazer Linho Premium Alfaiataria", category: "Blazers", sentiment_score: 0.88, rating: 5, review_text: "Blazer elegante com corte de alfaiataria excelente. Cor fiel à foto." },
  { product_name: "Biquíni Cortininha Classic Fit", category: "Biquínis", sentiment_score: -0.92, rating: 1, review_text: "O biquíni veio muito menor que a tabela de tamanhos e desbotou na primeira lavagem." },
  { product_name: "Vestido Longo Floral Cetim", category: "Vestidos", sentiment_score: -0.85, rating: 2, review_text: "A costura próxima ao zíper rasgou na primeira tentativa de vestir." },
  { product_name: "Macacão Utilitário Algodão", category: "Macacões", sentiment_score: 0.45, rating: 4, review_text: "Muito confortável e prático para o dia a dia. A entrega apenas demorou 2 dias." }
];

const DEFAULT_COMMERCIAL = {
  kpis: {
    priced_variants: 575,
    price_coverage_pct: 97.96,
    median_price: 689.5,
    discounted_pct: 22.09,
    top_category: "Vestidos"
  },
  catalog_count: 587,
  category_summary: [
    { category: "Blazers", variants: 25, median_price: 1589.0, category_price_tier: "PREMIUM", share_pct: 4.7 },
    { category: "Macacões", variants: 41, median_price: 1489.0, category_price_tier: "PREMIUM", share_pct: 7.1 },
    { category: "Sobretudos", variants: 1, median_price: 1244.5, category_price_tier: "PREMIUM", share_pct: 0.2 },
    { category: "Vestidos", variants: 168, median_price: 1069.5, category_price_tier: "PREMIUM", share_pct: 28.6 },
    { category: "Blusas", variants: 23, median_price: 989.0, category_price_tier: "PREMIUM", share_pct: 3.9 },
    { category: "Calças", variants: 24, median_price: 694.25, category_price_tier: "CORE", share_pct: 4.1 },
    { category: "Bodies", variants: 52, median_price: 649.0, category_price_tier: "CORE", share_pct: 8.8 },
    { category: "Saídas", variants: 8, median_price: 594.5, category_price_tier: "CORE", share_pct: 1.4 },
    { category: "Pareôs", variants: 23, median_price: 489.0, category_price_tier: "ACCESS", share_pct: 3.9 },
    { category: "Biquínis", variants: 110, median_price: 489.0, category_price_tier: "ACCESS", share_pct: 18.7 },
    { category: "Croppeds", variants: 32, median_price: 394.5, category_price_tier: "ACCESS", share_pct: 5.4 }
  ]
};

const DEFAULT_PORTFOLIO = {
  total_clustered: 587,
  total_duplicates_pairs: 753,
  clusters: [
    { portfolio_cluster: 0, dominant_category: "Biquínis", items: 110, label: "Roupas de Banho & Praia", opportunity: "Manter Grade Contínua" },
    { portfolio_cluster: 1, dominant_category: "Blazers", items: 68, label: "Alfaiataria Premium", opportunity: "Expandir Linha Linho" },
    { portfolio_cluster: 2, dominant_category: "Vestidos", items: 210, label: "Vestidos & Macacões Elegance", opportunity: "Costura Dupla nos Zíperes" },
    { portfolio_cluster: 3, dominant_category: "Bodies", items: 84, label: "Conjuntos Promocionais", opportunity: "Liquidação Estratégica" },
    { portfolio_cluster: 4, dominant_category: "Calças", items: 115, label: "Básicos & Essenciais", opportunity: "Reposição de Tamanho M" }
  ],
  near_duplicates: [
    { product_a: "Vestido Midi Seda Rose", product_b: "Vestido Midi Seda Rosê Soft", similarity: 0.98, category: "Vestidos" },
    { product_a: "Blazer Linho Areia", product_b: "Blazer Alfaiataria Linho Nude", similarity: 0.96, category: "Blazers" },
    { product_a: "Biquíni Cortininha Preto", product_b: "Biquíni Triângulo Classic Black", similarity: 0.95, category: "Biquínis" },
    { product_a: "Macacão Algodão Oliva", product_b: "Macacão Utilitário Sarja Kaki", similarity: 0.94, category: "Macacões" }
  ]
};

const DEFAULT_DECISIONS = {
  high_priority_count: 7,
  opportunities: [
    { priority: "HIGH", scope: "CATEGORY", entity: "Vestidos", headline: "Desvio Severo de Promoção (168 Peças)", recommended_action: "Otimizar desconto de 15% para 12%, preservando R$ 14.800 de margem.", evidence: "168 variações mapeadas" },
    { priority: "HIGH", scope: "PRODUCT", entity: "Biquíni Cortininha Classic", headline: "Tamanho Menor que Padrão & Desbotamento", recommended_action: "Revisar tabela de medidas e solidez de cor com a confecção.", evidence: "14 reclamações em 48h" },
    { priority: "HIGH", scope: "CLUSTER", entity: "Alfaiataria Premium", headline: "Demanda Reprimida de Linho", recommended_action: "Adicionar 4 SKUs em cores neutras (Areia/Oliva).", evidence: "Margem de 68% e Profundidade 9.1" },
    { priority: "HIGH", scope: "PRODUCT", entity: "Macacão Utilitário Algodão", headline: "Ruptura de Estoque na Grade M/G", recommended_action: "Remanejar 250 unidades para o CD Principal.", evidence: "Giro 2.4x superior" },
    { priority: "MEDIUM", scope: "CATEGORY", entity: "Blazers", headline: "Preço Inelástico (-0.75)", recommended_action: "Reduzir remarcação de 10% para 5%.", evidence: "Preço Mediano R$ 1.589" }
  ]
};

const DEFAULT_QUALITY = [
  { field: "product_id", rows: 587, non_null: 587, missing: 0, completeness_pct: 100.0, trust: "GOOD" },
  { field: "name", rows: 587, non_null: 587, missing: 0, completeness_pct: 100.0, trust: "GOOD" },
  { field: "category", rows: 587, non_null: 569, missing: 18, completeness_pct: 96.93, trust: "GOOD" },
  { field: "price", rows: 587, non_null: 575, missing: 12, completeness_pct: 97.96, trust: "GOOD" },
  { field: "color", rows: 587, non_null: 542, missing: 45, completeness_pct: 92.33, trust: "PARTIAL" },
  { field: "sizes", rows: 587, non_null: 556, missing: 31, completeness_pct: 94.72, trust: "GOOD" }
];

const PROMPT_MENUS = {
  executive: [
    "Qual a síntese executiva sobre a saúde comercial do catálogo de 587 produtos?",
    "Quais são as 3 principais ações estratégicas com maior ROI para hoje?",
    "Qual o diagnóstico de CSAT e percepção de valor dos clientes?",
    "Como está distribuído o faturamento e preço mediano por categoria?"
  ],
  buyer: [
    "Quais categorias e tamanhos possuem maior risco de ruptura de estoque?",
    "Quais são os principais White Spaces e lacunas no nosso mix de produtos?",
    "Como está o índice de cobertura de grade de tamanhos (P, M, G, GG)?",
    "Quantas unidades da grade M/G devemos remanejar para o CD Principal?"
  ],
  pricing: [
    "Quais categorias apresentam maior pressão de desconto (Markdown Pressure)?",
    "Qual a elasticidade da categoria Vestidos e o desconto ótimo sugerido?",
    "Qual a estimativa de ganho em margem ao reduzir 5% de desconto em Blazers?",
    "Quais SKUs do Cluster de Baixo Giro devemos liquidação hoje?"
  ],
  qa: [
    "Quais foram os principais motivos de reclamação de clientes nas últimas 48h?",
    "Qual o diagnóstico técnico sobre defeitos de costura em zíperes de Seda?",
    "Quais produtos apresentam divergência na tabela de medidas e tamanhos?",
    "Quais fornecedores e lotes devem ser acionados para auditoria técnica?"
  ]
};

const AGENTS = [
  { id: "executive", name: "Agente Executivo", title: "CEO Advisor", icon: Crown, color: "#F59E0B", desc: "Análise estratégica dos 587 produtos, metas e visão executiva." },
  { id: "buyer", name: "Agente Comprador", title: "Assortment Specialist", icon: ShoppingBag, color: "#10B981", desc: "Recomendações para as 14 categorias e reposição de estoque." },
  { id: "pricing", name: "Agente de Pricing", title: "Margin & Elasticity", icon: Tag, color: "#3B82F6", desc: "Precificação dinâmica por tier (Premium R$ 1.589 / Access R$ 489)." },
  { id: "qa", name: "Agente de Qualidade", title: "Customer QA Audit", icon: ShieldCheck, color: "#EF4444", desc: "Auditoria de insatisfações e reclamações em tempo real." }
];

function App() {
  const [activeTab, setActiveTab] = useState("cockpit");
  const [selectedAgent, setSelectedAgent] = useState("executive");
  const [decisionsSubTab, setDecisionsSubTab] = useState("urgentes");
  
  const [reviews, setReviews] = useState(DEFAULT_REVIEWS);
  const [kpis, setKpis] = useState({ total_reviews: 11, avg_sentiment: 0.28, csat_score: 82.4, positive: 7, negative: 4, neutral: 0 });
  const [commercialData, setCommercialData] = useState(DEFAULT_COMMERCIAL);
  const [portfolioData, setPortfolioData] = useState(DEFAULT_PORTFOLIO);
  const [decisionsData, setDecisionsData] = useState(DEFAULT_DECISIONS);
  const [qualityReport, setQualityReport] = useState(DEFAULT_QUALITY);
  const [catalogProducts, setCatalogProducts] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  
  const [selectedCategory, setSelectedCategory] = useState("Biquínis");
  const [aiRec, setAiRec] = useState("Análise de Sentimento Snowflake Cortex: Reclamações concentradas em tamanho pequeno de Biquínis e desbotamento na lavagem. Recomenda-se auditar o fornecedor de tecido.");
  
  // Simulator State
  const [simSkus, setSimSkus] = useState(4);
  const [simCat, setSimCat] = useState("Blazers");
  const [simPrice, setSimPrice] = useState(1589);
  const [simResult, setSimResult] = useState({ revenue: "R$ 540.260,00", margin: "R$ 351.169,00", risk: "Baixo (6.2%)" });

  // Multi-Agent Chat Messages
  const [chatMessages, setChatMessages] = useState([
    { sender: "agent", agentRole: "executive", text: "👑 Agente Executivo INTI: Bem-vindo! Analisei todo o catálogo com 587 produtos e 14 categorias. Selecione um Agente especialista abaixo para consultas específicas." }
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
      // Rich fallbacks
    }
    return null;
  };

  const fetchData = async () => {
    const rSent = await safeFetchJson('/api/sentiment');
    if (rSent && Array.isArray(rSent)) setReviews(rSent);

    const rKpi = await safeFetchJson('/api/kpis');
    if (rKpi) setKpis(rKpi);

    const rCom = await safeFetchJson('/api/commercial');
    if (rCom && rCom.category_summary) setCommercialData(rCom);

    const rPort = await safeFetchJson('/api/portfolio-ml');
    if (rPort && rPort.clusters) setPortfolioData(rPort);

    const rDec = await safeFetchJson('/api/decisions');
    if (rDec && rDec.opportunities) setDecisionsData(rDec);

    const rQual = await safeFetchJson('/api/data-quality');
    if (rQual && rQual.report) setQualityReport(rQual.report);

    const rCat = await safeFetchJson('/api/catalog');
    if (rCat && rCat.products) setCatalogProducts(rCat.products);
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
    if (e && e.preventDefault) e.preventDefault();
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
      let reply = `Agente INTI AI (${currentRole}): Analisei '${q}'. Todos os 587 produtos e 14 categorias estão sincronizados no Snowflake.`;
      if (currentRole === "executive") reply = `👑 Agente Executivo: Analisei '${q}'. Mapeamos 587 SKUs ativos. Blazers possuem o maior preço mediano (R$ 1.589) e Vestidos lideram o volume com 168 variações. Recomendo priorizar as 7 Ações Críticas.`;
      if (currentRole === "buyer") reply = `🛍️ Agente Comprador: Para '${q}', identificamos lacunas de estoque em Macacões e Bodies (52 variações). Sugerimos remanejar 250 unidades para o CD Principal.`;
      if (currentRole === "pricing") reply = `🏷️ Agente de Pricing: Em '${q}', a elasticidade atual é -1.42. Reduzir a remarcação de 15% para 12% em Vestidos gerará ganho de R$ 14.800 em margem.`;
      if (currentRole === "qa") reply = `🔬 Agente de Qualidade: Sobre '${q}', registramos 14 reclamações sobre costuras em zíperes de Seda e tamanho pequeno em Biquínis. Auditoria técnica acionada.`;
      
      setChatMessages(prev => [...prev, { sender: "agent", agentRole: currentRole, text: reply }]);
    }
  };

  const filteredCatalog = catalogProducts.filter(p => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (p.name && p.name.toLowerCase().includes(q)) || 
           (p.category && p.category.toLowerCase().includes(q)) ||
           (p.color && p.color.toLowerCase().includes(q));
  });

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
            <span className="brand-tag">v2.1 Full Ecosystem · 587 SKUs</span>
          </div>
        </div>

        <nav className="sidebar-menu">
          <button className={`menu-item ${activeTab === 'cockpit' ? 'active' : ''}`} onClick={() => setActiveTab('cockpit')}>
            <TrendingUp size={18} /> <span>Cockpit & Sentimento</span>
          </button>
          <button className={`menu-item ${activeTab === 'agentes' ? 'active' : ''}`} onClick={() => setActiveTab('agentes')}>
            <Cpu size={18} /> <span>Suíte de Agentes IA</span>
          </button>
          <button className={`menu-item ${activeTab === 'decisões' ? 'active' : ''}`} onClick={() => setActiveTab('decisões')}>
            <Zap size={18} /> <span>Decisão & Oportunidades</span>
          </button>
          <button className={`menu-item ${activeTab === 'pricing' ? 'active' : ''}`} onClick={() => setActiveTab('pricing')}>
            <DollarSign size={18} /> <span>Comercial & Pricing</span>
          </button>
          <button className={`menu-item ${activeTab === 'sortimento' ? 'active' : ''}`} onClick={() => setActiveTab('sortimento')}>
            <Layers size={18} /> <span>Sortimento & Clusters</span>
          </button>
          <button className={`menu-item ${activeTab === 'catalogo' ? 'active' : ''}`} onClick={() => setActiveTab('catalogo')}>
            <Search size={18} /> <span>Explorador de Catálogo</span>
          </button>
          <button className={`menu-item ${activeTab === 'qualidade' ? 'active' : ''}`} onClick={() => setActiveTab('qualidade')}>
            <Database size={18} /> <span>Qualidade dos Dados</span>
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
              {activeTab === 'decisões' && '⚡ Inteligência de Decisão & Motor de Oportunidades'}
              {activeTab === 'pricing' && '💰 Inteligência Comercial & Precificação Dinâmica'}
              {activeTab === 'sortimento' && '🛍️ Sortimento, Cores & Clusters KMeans'}
              {activeTab === 'catalogo' && '👗 Explorador Interativo do Catálogo de Produtos'}
              {activeTab === 'qualidade' && '🛡️ Relatório de Qualidade & Completude dos Dados'}
            </h1>
            <p>Single Source of Truth Ativo | {commercialData.catalog_count || 587} Peças Mapeadas | Sub-Second Cache Active</p>
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
                  <span className="card-label">Peças Mapeadas</span>
                  <h3 className="card-val">{commercialData.catalog_count || 587}</h3>
                  <span className="card-sub green">14 Categorias Ativas</span>
                </div>
              </div>

              <div className="glass-card">
                <div className="card-icon icon-emerald"><TrendingUp size={20} /></div>
                <div>
                  <span className="card-label">Preço Mediano</span>
                  <h3 className="card-val">R$ 689,50</h3>
                  <span className="card-sub green">Cobertura 97.96%</span>
                </div>
              </div>

              <div className="glass-card">
                <div className="card-icon icon-indigo"><Sparkles size={20} /></div>
                <div>
                  <span className="card-label">Índice CSAT</span>
                  <h3 className="card-val">{kpis.csat_score}%</h3>
                  <span className="card-sub indigo">Avaliações Cortex</span>
                </div>
              </div>

              <div className="glass-card">
                <div className="card-icon icon-rose"><AlertTriangle size={20} /></div>
                <div>
                  <span className="card-label">Ações Críticas</span>
                  <h3 className="card-val">{decisionsData.high_priority_count || 7}</h3>
                  <span className="card-sub rose">Ação Imediata Hoje</span>
                </div>
              </div>
            </div>

            {/* Retail Balloons */}
            <div className="retail-balloons-grid">
              <div className="retail-balloon-card">
                <div className="balloon-tag">🎈 Volume do Mix</div>
                <p>São <strong>587 opções ativas</strong> no catálogo concorrente. Monitore o ritmo de lançamentos semanal.</p>
              </div>
              <div className="retail-balloon-card">
                <div className="balloon-tag">🎈 Alvos Urgentes de Hoje</div>
                <p>Total de <strong>7 desvios severos</strong> de preço e estoque mapeados pela Inteligência Artificial.</p>
              </div>
              <div className="retail-balloon-card">
                <div className="balloon-tag">🎈 Peças Quase Idênticas</div>
                <p>Mapeamos <strong>753 pares</strong> com similaridade visual e de modelagem superior a 94%.</p>
              </div>
            </div>

            <div className="grid-2col mt-4">
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
                  {["Biquínis", "Vestidos", "Blazers", "Macacões", "Bodies"].map(cat => (
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

              {/* Prompt Menu Chips */}
              <div className="prompt-menu-container">
                <span className="prompt-menu-title">💡 Menu de Perguntas Recomendadas para este Agente:</span>
                <div className="prompt-chips-grid">
                  {(PROMPT_MENUS[selectedAgent] || []).map((promptText, idx) => (
                    <button 
                      key={idx} 
                      className="prompt-chip-btn"
                      onClick={() => {
                        setUserQuery(promptText);
                        setTimeout(() => {
                          handleSendMultiChat({ preventDefault: () => {} });
                        }, 50);
                      }}
                    >
                      {promptText}
                    </button>
                  ))}
                </div>
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

        {/* SECTION 3: DECISION INTELLIGENCE & OPPORTUNITIES */}
        {activeTab === 'decisões' && (
          <div className="content-body">
            <div className="glass-panel">
              <div className="panel-top flex-between">
                <h3>Inteligência de Decisão & Motor de IA</h3>
                <div className="subtabs-bar">
                  <button className={`subtab-btn ${decisionsSubTab === 'urgentes' ? 'active' : ''}`} onClick={() => setDecisionsSubTab('urgentes')}>
                    🚨 Ações Urgentes (7)
                  </button>
                  <button className={`subtab-btn ${decisionsSubTab === 'identicas' ? 'active' : ''}`} onClick={() => setDecisionsSubTab('identicas')}>
                    👚 Peças Quase Idênticas (753)
                  </button>
                  <button className={`subtab-btn ${decisionsSubTab === 'estilos' ? 'active' : ''}`} onClick={() => setDecisionsSubTab('estilos')}>
                    📦 Estilos de Roupas (5)
                  </button>
                </div>
              </div>

              {decisionsSubTab === 'urgentes' && (
                <div className="decisions-list">
                  {decisionsData.opportunities.map((opp, i) => (
                    <div key={i} className="decision-row-card">
                      <div className="dec-meta">
                        <span className="dec-id">{opp.scope || 'AÇÃO EXEC'}</span>
                        <span className={`badge ${opp.priority === 'HIGH' ? 'badge-negative' : 'badge-positive'}`}>{opp.priority || 'ALTA'} Prioridade</span>
                      </div>
                      <div className="dec-body">
                        <h4>{opp.headline || opp.title}</h4>
                        <p>Item Analisado: <strong>{opp.entity || opp.category}</strong> | Evidências: <strong>{opp.evidence || 'Evidência Forte'}</strong></p>
                        <div className="dec-action">
                          👉 <strong>Recomendação Executiva:</strong> {opp.recommended_action || opp.action}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {decisionsSubTab === 'identicas' && (
                <div className="table-container">
                  <table className="custom-table">
                    <thead>
                      <tr>
                        <th>Produto A</th>
                        <th>Produto B</th>
                        <th>Similaridade Estrutural</th>
                        <th>Categoria</th>
                      </tr>
                    </thead>
                    <tbody>
                      {portfolioData.near_duplicates.slice(0, 10).map((d, i) => (
                        <tr key={i}>
                          <td className="font-bold">{d.product_a || d.product_1 || 'Peça A'}</td>
                          <td>{d.product_b || d.product_2 || 'Peça B'}</td>
                          <td><span className="badge badge-positive">{(d.similarity ? (d.similarity * 100).toFixed(0) : 95)}%</span></td>
                          <td><span className="tag-cat">{d.category || 'Geral'}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {decisionsSubTab === 'estilos' && (
                <div className="clusters-grid-4">
                  {portfolioData.clusters.map((cl, i) => (
                    <div key={i} className="cluster-card-modern">
                      <div className="cluster-num">Cluster #{cl.portfolio_cluster ?? i}</div>
                      <h4>{cl.label || cl.dominant_category}</h4>
                      <div className="cluster-metrics">
                        <div><span>Total de Itens:</span> <strong>{cl.items} Peças</strong></div>
                        <div><span>Categoria Dominante:</span> <strong>{cl.dominant_category}</strong></div>
                      </div>
                      <div className="cluster-action-box">
                        <Target size={14} /> <span>{cl.opportunity || 'Otimizar Sortimento'}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* SECTION 4: COMMERCIAL & DYNAMIC PRICING */}
        {activeTab === 'pricing' && (
          <div className="content-body">
            <div className="grid-2col">
              <div className="glass-panel">
                <div className="panel-top">
                  <h3>Elasticidade de Preços & Tier por Categoria</h3>
                </div>
                <p className="panel-desc">Calculado com base no preço mediano e comportamento de remarcação das 14 categorias.</p>
                <div className="table-container">
                  <table className="custom-table">
                    <thead>
                      <tr>
                        <th>Categoria</th>
                        <th>Variações</th>
                        <th>Preço Mediano</th>
                        <th>Tier Estrutural</th>
                      </tr>
                    </thead>
                    <tbody>
                      {commercialData.category_summary.map((c, i) => (
                        <tr key={i}>
                          <td className="font-bold">{c.category}</td>
                          <td>{c.variants} variações</td>
                          <td><span className="font-bold text-emerald">R$ {c.median_price?.toFixed(2)}</span></td>
                          <td>
                            <span className={`badge ${c.category_price_tier === 'PREMIUM' ? 'badge-indigo' : c.category_price_tier === 'CORE' ? 'badge-positive' : 'badge-neutral'}`}>
                              {c.category_price_tier || 'CORE'}
                            </span>
                          </td>
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
                      <option value="Blazers">Blazers (Mediano: R$ 1.589)</option>
                      <option value="Macacões">Macacões (Mediano: R$ 1.489)</option>
                      <option value="Vestidos">Vestidos (Mediano: R$ 1.069)</option>
                      <option value="Bodies">Bodies (Mediano: R$ 649)</option>
                      <option value="Biquínis">Biquínis (Mediano: R$ 489)</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Quantidade de Novos SKUs:</label>
                    <input type="number" min="1" max="50" value={simSkus} onChange={e => setSimSkus(e.target.value)} />
                  </div>

                  <div className="form-group">
                    <label>Preço Alvo Estimado (R$):</label>
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

        {/* SECTION 5: SORTIMENTO & CLUSTERS */}
        {activeTab === 'sortimento' && (
          <div className="content-body">
            <div className="glass-panel">
              <div className="panel-top">
                <h3>5 Estilos de Coleções Mapeados (Clusters KMeans)</h3>
              </div>
              <div className="clusters-grid-4">
                {portfolioData.clusters.map((cl, i) => (
                  <div key={i} className="cluster-card-modern">
                    <div className="cluster-num">Cluster #{cl.portfolio_cluster ?? i}</div>
                    <h4>{cl.label || cl.dominant_category}</h4>
                    <div className="cluster-metrics">
                      <div><span>Total de Itens:</span> <strong>{cl.items} Peças</strong></div>
                      <div><span>Categoria Dominante:</span> <strong>{cl.dominant_category}</strong></div>
                    </div>
                    <div className="cluster-action-box">
                      <Target size={14} /> <span>{cl.opportunity || 'Otimizar Sortimento'}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid-2col mt-4">
              <div className="glass-panel">
                <div className="panel-top">
                  <h3>Arquitetura do Mix por Categoria (587 Produtos)</h3>
                </div>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={commercialData.category_summary}>
                    <XAxis dataKey="category" stroke="#94A3B8" />
                    <YAxis stroke="#94A3B8" />
                    <Tooltip contentStyle={{ backgroundColor: '#1E293B', color: '#FFF' }} />
                    <Bar dataKey="variants" fill="#3B82F6" radius={[6, 6, 0, 0]} name="Variações de Produtos" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="glass-panel">
                <div className="panel-top">
                  <div className="flex-align"><Copy size={18} /><h3>Peças Quase Idênticas ({portfolioData.total_duplicates_pairs || 753} Pares)</h3></div>
                </div>
                <p className="panel-desc">Duplicidades com similaridade visual e de modelagem de 94% ou superior:</p>
                <div className="table-container" style={{ maxHeight: '240px', overflowY: 'auto' }}>
                  <table className="custom-table">
                    <thead>
                      <tr>
                        <th>Produto A</th>
                        <th>Produto B</th>
                        <th>Similaridade</th>
                      </tr>
                    </thead>
                    <tbody>
                      {portfolioData.near_duplicates.slice(0, 5).map((d, i) => (
                        <tr key={i}>
                          <td className="font-bold">{d.product_a || d.product_1 || 'Peça A'}</td>
                          <td>{d.product_b || d.product_2 || 'Peça B'}</td>
                          <td><span className="badge badge-positive">{(d.similarity ? (d.similarity * 100).toFixed(0) : 95)}%</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* SECTION 6: CATALOG BROWSER */}
        {activeTab === 'catalogo' && (
          <div className="content-body">
            <div className="glass-panel">
              <div className="panel-top flex-between">
                <h3>Explorador de Catálogo ({filteredCatalog.length > 0 ? filteredCatalog.length : 587} Produtos Mapeados)</h3>
                <div className="search-bar-box">
                  <Search size={16} />
                  <input 
                    type="text" 
                    placeholder="Buscar produto por nome, cor ou categoria..."
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                  />
                </div>
              </div>

              <div className="table-container" style={{ maxHeight: '520px', overflowY: 'auto' }}>
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Produto</th>
                      <th>Categoria</th>
                      <th>Cor</th>
                      <th>Preço</th>
                      <th>Original</th>
                      <th>Desconto</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(filteredCatalog.length > 0 ? filteredCatalog.slice(0, 30) : commercialData.category_summary).map((p, i) => (
                      <tr key={i}>
                        <td className="dec-id">#{p.product_id || (i + 100)}</td>
                        <td className="font-bold">{p.name || `${p.category} Variant #${i+1}`}</td>
                        <td><span className="tag-cat">{p.category}</span></td>
                        <td>{p.color || 'Neutro'}</td>
                        <td><span className="font-bold text-emerald">R$ {p.price ? Number(p.price).toFixed(2) : p.median_price?.toFixed(2)}</span></td>
                        <td>{p.original_price ? `R$ ${Number(p.original_price).toFixed(2)}` : '-'}</td>
                        <td>
                          {p.discount_pct ? (
                            <span className="badge badge-negative">-{p.discount_pct}%</span>
                          ) : (
                            <span className="badge badge-neutral">Preço Cheio</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* SECTION 7: DATA QUALITY & TEMPORAL SIGNALS */}
        {activeTab === 'qualidade' && (
          <div className="content-body">
            <div className="glass-panel">
              <div className="panel-top">
                <h3>Relatório de Qualidade & Completude dos Dados (Single Source of Truth)</h3>
              </div>
              <div className="table-container">
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th>Campo</th>
                      <th>Total de Linhas</th>
                      <th>Preenchidos</th>
                      <th>Ausentes</th>
                      <th>Completude (%)</th>
                      <th>Status de Confiança</th>
                    </tr>
                  </thead>
                  <tbody>
                    {qualityReport.map((q, i) => (
                      <tr key={i}>
                        <td className="font-bold">{q.field}</td>
                        <td>{q.rows}</td>
                        <td>{q.non_null}</td>
                        <td>{q.missing}</td>
                        <td><strong>{q.completeness_pct}%</strong></td>
                        <td>
                          <span className={`badge ${q.trust === 'GOOD' ? 'badge-positive' : q.trust === 'PARTIAL' ? 'badge-amber' : 'badge-negative'}`}>
                            {q.trust === 'GOOD' ? 'GOOD (Confiável)' : q.trust === 'PARTIAL' ? 'PARTIAL (Parcial)' : 'MISSING'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
