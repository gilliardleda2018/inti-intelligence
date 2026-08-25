from __future__ import annotations
import numpy as np
import pandas as pd

try:
    from sklearn.cluster import KMeans
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.metrics import silhouette_score
    from sklearn.neighbors import NearestNeighbors
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import TfidfVectorizer
except ImportError as exc:
    raise ImportError("Portfolio ML requires scikit-learn. Run: python -m pip install scikit-learn") from exc


def _num(s): return pd.to_numeric(s, errors="coerce")
def _size_count(v):
    if pd.isna(v): return 0
    return len([x for x in str(v).replace(",","|").split("|") if x.strip()])


def _prepare(catalog: pd.DataFrame) -> pd.DataFrame:
    df=catalog.copy().reset_index(drop=True)
    for c in ["name","category","color","sizes","description"]:
        if c not in df: df[c]="Unknown"
        df[c]=df[c].fillna("Unknown").astype(str)
    for c in ["price","original_price","discount_pct"]:
        if c not in df: df[c]=np.nan
        df[c]=_num(df[c])
    df["size_count"]=df["sizes"].apply(_size_count)
    cat_med=df.groupby("category")["price"].transform("median")
    df["price_vs_category"]=np.where(cat_med>0,df["price"]/cat_med,np.nan)
    df["discount_pct"]=df["discount_pct"].fillna(0)
    return df


def _matrix(df):
    numeric=["price","original_price","discount_pct","size_count","price_vs_category"]
    categorical=["category","color"]
    pre=ColumnTransformer([
        ("num",Pipeline([("imp",SimpleImputer(strategy="median")),("scale",StandardScaler())]),numeric),
        ("cat",Pipeline([("imp",SimpleImputer(strategy="most_frequent")),
                         ("oh",OneHotEncoder(handle_unknown="ignore"))]),categorical),
        ("text_name",TfidfVectorizer(max_features=20, stop_words=None),"name"),
        ("text_desc",TfidfVectorizer(max_features=25, stop_words=None),"description")
    ])
    X=pre.fit_transform(df)
    return X,pre


def _choose_k(X,n):
    if n < 8: return max(2,min(3,n-1)), None
    upper=min(10,max(3,int(np.sqrt(n))))
    best_k,best_score=3,-1
    for k in range(3,upper+1):
        labels=KMeans(n_clusters=k,random_state=42,n_init=10).fit_predict(X)
        if len(set(labels))<2: continue
        score=silhouette_score(X,labels,sample_size=min(500,n),random_state=42)
        if score>best_score: best_k,best_score=k,float(score)
    return best_k,best_score


def portfolio_ml(catalog: pd.DataFrame) -> tuple[pd.DataFrame,dict]:
    df=_prepare(catalog)
    if len(df)<3:
        return df,{"products":len(df),"clusters":0,"silhouette":None}
    X,_=_matrix(df)
    k,sil=_choose_k(X,len(df))
    km=KMeans(n_clusters=k,random_state=42,n_init=20)
    df["portfolio_cluster"]=km.fit_predict(X).astype(int)

    # 2D latent map for visualization only.
    dims=min(2,max(1,X.shape[1]-1))
    if dims==2:
        emb=TruncatedSVD(n_components=2,random_state=42).fit_transform(X)
        df["ml_x"],df["ml_y"]=emb[:,0],emb[:,1]
    else:
        arr=X.toarray() if hasattr(X,"toarray") else np.asarray(X)
        df["ml_x"]=arr[:,0]; df["ml_y"]=0.0

    counts=df["portfolio_cluster"].value_counts()
    df["cluster_size"]=df["portfolio_cluster"].map(counts).astype(int)
    stats={
        "products":int(len(df)),"clusters":int(k),
        "silhouette":None if sil is None else round(sil,4),
        "largest_cluster":int(counts.max()),
        "smallest_cluster":int(counts.min())
    }
    return df,stats


def similarity_neighbors(catalog: pd.DataFrame, n_neighbors:int=6) -> pd.DataFrame:
    df=_prepare(catalog)
    if len(df)<2: return pd.DataFrame()
    X,_=_matrix(df)
    k=min(n_neighbors+1,len(df))
    nn=NearestNeighbors(n_neighbors=k,metric="cosine").fit(X)
    dist,idx=nn.kneighbors(X)
    rows=[]
    for i in range(len(df)):
        rank=0
        for d,j in zip(dist[i],idx[i]):
            if i==j: continue
            rank+=1
            rows.append({
                "product":df.loc[i,"name"],"category":df.loc[i,"category"],
                "neighbor":df.loc[j,"name"],"neighbor_category":df.loc[j,"category"],
                "rank":rank,"similarity_pct":round(max(0,1-float(d))*100,2)
            })
    return pd.DataFrame(rows)


def near_duplicate_radar(catalog: pd.DataFrame, threshold:float=92.0) -> pd.DataFrame:
    n=similarity_neighbors(catalog,5)
    if n.empty: return n
    out=n[(n["rank"]<=3)&(n["similarity_pct"]>=threshold)].copy()
    # de-duplicate symmetric pairs
    out["_pair"]=out.apply(lambda r:"||".join(sorted([str(r["product"]),str(r["neighbor"])])),axis=1)
    return out.sort_values("similarity_pct",ascending=False).drop_duplicates("_pair").drop(columns="_pair").reset_index(drop=True)


def cluster_profiles(catalog: pd.DataFrame) -> pd.DataFrame:
    df,stats=portfolio_ml(catalog)
    if df.empty or "portfolio_cluster" not in df: return pd.DataFrame()
    prof=df.groupby("portfolio_cluster").agg(
        items=("name","count"),
        median_price=("price","median"),
        mean_discount_pct=("discount_pct","mean"),
        median_sizes=("size_count","median"),
        dominant_category=("category",lambda x:x.value_counts().index[0]),
        dominant_color=("color",lambda x:x.value_counts().index[0])
    ).reset_index()
    prof["share_pct"]=(prof["items"]/len(df)*100).round(2)
    return prof.sort_values("items",ascending=False).reset_index(drop=True)


def white_space_candidates(catalog: pd.DataFrame) -> pd.DataFrame:
    df,stats=portfolio_ml(catalog)
    if df.empty: return pd.DataFrame()
    prof=cluster_profiles(catalog)
    # Conservative "sparse portfolio zone": small clusters only, not a demand opportunity claim.
    cutoff=max(3,int(len(df)*0.05))
    sparse=prof[prof["items"]<=cutoff].copy()
    if sparse.empty: return sparse
    sparse["signal"]="SPARSE_PORTFOLIO_ZONE"
    sparse["interpretation"]="Região pouco ocupada no espaço estrutural do catálogo; requer validação de demanda antes de tratar como oportunidade."
    return sparse
