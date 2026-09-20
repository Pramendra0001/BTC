# BTC-SHIELD Relational Link Analysis Graph Schema

**Engine:** NetworkX Multigraph & In-Memory Centrality Engine  
**Frontend Visualizer:** Cytoscape.js directed multigraph  
**Format:** Cytoscape.js standard JSON (`nodes`, `edges`)  

---

## 1. Graph Ontology

BTC-SHIELD models Bitcoin activity as a heterogeneous, directed property multigraph $G = (V, E)$.

### 1.1 Node Types ($V$)

| Node Type | Prefix Format | Color Code | Cytoscape Shape | Properties |
|---|---|---|---|---|
| `WALLET` | `WALLET:<address>` | `#2563eb` (Blue) | Ellipse | `address`, `tx_count`, `total_sent`, `total_received`, `anomaly_score`, `is_center` |
| `TRANSACTION` | `TX:<txid>` | `#9333ea` (Purple) | Round Rectangle | `txid`, `fee`, `timestamp`, `script_type`, `total_input`, `total_output` |
| `IP` | `IP:<ip_address>` | `#059669` (Emerald) | Diamond | `ip_address`, `observation_count`, `country`, `asn` |
| `ASN` | `ASN:<asn_number>` | `#d97706` (Amber) | Hexagon | `asn_number`, `name`, `country_count`, `ip_count` |
| `COUNTRY` | `COUNTRY:<iso_code>` | `#0891b2` (Cyan) | Octagon | `code`, `country_name` |

### 1.2 Edge Types ($E$)

| Edge Type | Source Node | Target Node | Color | Line Style | Description |
|---|---|---|---|---|---|
| `INPUT_OF` | `WALLET` | `TRANSACTION` | `#3b82f6` | Solid Arrow | Identifies the wallet providing inputs to a transaction |
| `OUTPUT_OF` | `TRANSACTION` | `WALLET` | `#8b5cf6` | Solid Arrow | Identifies the recipient wallet receiving outputs |
| `OBSERVED_FROM` | `TRANSACTION` | `IP` | `#10b981` | Dashed Arrow | Correlates on-chain transaction with peer IP observation |
| `COUNTERPARTY` | `WALLET` | `WALLET` | `#eab308` | Dotted Arrow | Direct counterparty transfer link |
| `BELONGS_TO_ASN` | `IP` | `ASN` | `#f59e0b` | Dotted Line | Network routing provider association |
| `LOCATED_IN` | `IP` | `COUNTRY` | `#06b6d4` | Dotted Line | Geographic spatial jurisdiction |

---

## 2. Graph Algorithms & Centrality Metrics

### 2.1 Degree Centrality
Measures immediate connectivity and laundering fan-out:
$$C_D(v) = \frac{\text{deg}(v)}{|V| - 1}$$

### 2.2 PageRank Centrality
Calculates probabilistic significance within the transaction network:
$$PR(u) = \frac{1 - d}{|V|} + d \sum_{v \in B_u} \frac{PR(v)}{L(v)}$$
Damping factor $d = 0.85$, maximum iterations $= 100$.

### 2.3 Shortest Path Traversal
Identifies the laundering path connecting a source wallet to a target wallet or cash-out exchange using bidirectional Dijkstra shortest path analysis.
