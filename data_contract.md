# INTI Intelligence — Contrato mínimo de dados v0.1

## Pedidos
- order_id
- order_datetime
- customer_id_hash
- channel
- city
- state
- gross_value
- discount_value
- net_value
- order_status

## Itens
- order_id
- sku
- product_id
- product_name
- collection
- category
- color
- size
- quantity
- list_price
- sale_price
- discount

## Estoque
- snapshot_datetime
- sku
- location
- on_hand
- reserved
- available

## Produtos
- sku
- product_id
- collection
- category
- color
- size
- launch_date
- cost (se disponível)
- list_price

## Trocas/devoluções
- order_id
- sku
- event_date
- event_type
- reason

## Privacidade
Para o MVP analítico não são necessários nome, CPF, telefone ou e-mail. O identificador do cliente deve ser pseudonimizado/hash.
