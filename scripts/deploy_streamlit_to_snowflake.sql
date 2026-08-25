-- =====================================================================
-- SCRIPT DE IMPLANTAÇÃO — STREAMLIT IN SNOWFLAKE (SiS)
-- =====================================================================
-- Este arquivo contém os comandos DQL/DDL para implantar o dashboard
-- do INTI Intelligence diretamente na sua conta corporativa do Snowflake.

-- 1. Criação do Stage de Arquivos do Painel
CREATE STAGE IF NOT EXISTS INTI_STAGE;

-- [Nota] Para fazer o upload dos arquivos do projeto local para o stage,
-- você pode executar os comandos PUT abaixo via CLI (SnowSQL) ou carregá-los
-- diretamente no painel web (Snowsight) na aba 'Stages':
--
-- PUT file://./dashboard/app.py @INTI_STAGE/dashboard/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
-- PUT file://./src/inti_intelligence/*.py @INTI_STAGE/dashboard/src/inti_intelligence/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- 2. Criação do Warehouse Otimizado (Caso não exista)
-- Configurado como XSMALL com auto-suspensão em 60s para economizar a cota de $400
CREATE WAREHOUSE IF NOT EXISTS INTI_WH
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  COMMENT = 'Warehouse otimizado para o INTI Intelligence Dashboard';

-- 3. Criação da Aplicação Streamlit no Snowflake
-- Isso publica o frontend diretamente no console do Snowflake, acessível via url segura.
CREATE OR REPLACE STREAMLIT INTI_DASHBOARD
  ROOT_LOCATION = '@INTI_STAGE/dashboard'
  MAIN_FILE = 'app.py'
  QUERY_WAREHOUSE = 'INTI_WH'
  COMMENT = 'Painel Executivo e Técnico do INTI Intelligence';

-- 4. Permissões de Acesso para outros usuários/funções
-- GRANT USAGE ON STREAMLIT INTI_DASHBOARD TO ROLE ANALYST;
