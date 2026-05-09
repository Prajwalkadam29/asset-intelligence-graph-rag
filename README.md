# **Asset Intelligence Graph-RAG for Smart Manufacturing**

This project implements a **full digital thread intelligence system** combining:

* **Neo4j knowledge graph** (assemblies → parts → specs → embeddings)
* **Hybrid RAG retrieval engine**
* **Graph-aware LLM reasoning**
* **Compatibility scoring model for mechanical components**
* **FastAPI backend**
* **React frontend**
* **YAML ingestion + document storage**

It supports **natural-language engineering queries**, **part replacement suggestions**, **compatibility evaluation**, and **intelligent search** across manufacturing assemblies.

This is essentially a **mini industrial PLM + RAG + graph** system.

---

# **Data Model — The Digital Thread Knowledge Graph**

### 1. **Product Layer**

* Each product is a digital entity in Neo4j.
* Stores:

  * Name, SKU, description
  * Embedding (for product-level semantic retrieval)

Example:
**Industrial Lathe Machine**

---

### 2. **Assembly Layer**

Automatically generated from part categories using an `ASSEMBLY_MAP`, e.g.:

* **Spindle Assembly**
* **Z Axis Assembly**
* **X Axis Assembly**
* **Tailstock Assembly**
* **Mold System Assembly**
* **Electronics Assembly**

Assemblies are shared across parts and products.

Graph structure:

```
(Product) —[:HAS_ASSEMBLY]→ (Assembly) —[:HAS_PART]→ (Part)
```

---

### 3. **Parts**

Each part stores:

* `part_id`, `name`, `category`, `description`
* **Embedding (384-D)** using gte-small
* **Specs** (thread size, diameter, pitch, torque, etc.)
* **Children** for hierarchical structure (subcomponents)

Graph:

```
(Part) —[:HAS_CHILD]→ (Part)
(Part) —[:HAS_SPEC]→ (Spec)
```

---

### 4. **Specs (Node-Key Unique)**

Specs are stored as:

```
(key, value, unit)
```

With uniqueness enforced via a **NODE KEY constraint**.

This allows powerful spec-level queries like:

```
MATCH (p:Part)-[:HAS_SPEC]->(s:Spec {key:"pitch", value:5})
```

---

# **Ingestion Pipeline**

### YAML Ingestion

User uploads a YAML file:

```
product:
  name: Industrial Lathe Machine
  description: ...

parts:
  - part_id: SPINDLE-MT5-38HOLE
    category: Spindle
    specs:
      - key: "thread"
        value: "M45"
```

The ingestor:

1. Creates/updates product
2. Creates assemblies
3. Creates part nodes
4. Embeds each part's name + description
5. Stores specs (forcing non-null units)
6. Builds parent-child relationships recursively

This yields a **consistent, hierarchical digital twin**.

---

# **Retrieval Engine (Graph-RAG)**

This is one of the most advanced parts of the system.

## **Step 1: Embed the user question**

Using the same 384-D embedding model as parts.

---

## **Step 2: Perform Hybrid Retrieval**

Two searches run in parallel:

### **A. Vector semantic search**

```
CALL db.index.vector.queryNodes(
  'part_embedding_index',
  $k,
  $embedding
)
```

Retrieves semantically relevant parts even if keywords are missing.

---

### **B. Full-text search**

```
CALL db.index.fulltext.queryNodes(
  'part_fulltext_idx',
  $query
)
```

Retrieves keyword matches with fuzzy ranking.

---

## **Step 3: Filter by product or assembly**

We enforce digital-thread scoping:

* Only show parts that belong to the selected product
* Or selected assembly

---

## **Step 4: Merge and re-rank results**

We combine vector + keyword results, keeping only the **highest score per part_id**.

---

## **Step 5: Enrich results**

We fetch:

* Specs
* Product associations
* Assembly placement

---

## **Step 6: Fetch mutual compatibility edges**

If retrieved parts are known compatible, we display:

```
A ↔ B: score 0.73 — pitch matches; same assembly; compatible torque range
```

---

## **Step 7: LLM answer synthesis**

The LLM receives:

* Top retrieved parts
* Graph structure
* Specs
* Compatibility edges

It generates a structured, human-like engineering answer.

---

# ⚙️ **Compatibility Scoring Model — Why It’s Unique**

The compatibility model compares two parts (existing vs existing, or new vs existing) along **four dimensions**, each independently computed:

---

## **1. Mechanical Similarity (0–1)**

Checks:

* diameters
* lengths
* pitches
* threads
* torque ratings
* fits and tolerances

Scoring formula:

```
mechanical_score = weighted match of overlapping mechanical specs
```

---

## **2. Functional Similarity (0–1)**

Checks:

* part category
* assembly role
* operational purpose
* motion profile
* intended load path

E.g., two ballscrews functionally similar even if dimensions differ.

---

## **3. Semantic Similarity (0–1)**

Embedding distance between part descriptions.

This is extremely useful when specs are missing.

---

## **4. Hierarchical Similarity (0–1)**

Checks:

* Are both parts in the same assembly?
* Same subassembly?
* Do they share a parent/child?

Example:

```
Spindle Nut ↔ Spindle Shaft → HIGH
Ballscrew ↔ Tailstock → LOW
```

---

## **Final Score**

```
final_score = (0.35 * mechanical)
            + (0.25 * functional)
            + (0.25 * semantic)
            + (0.15 * hierarchy)
```

We also store:

```
explanations: ["same pitch", "same spindle assembly", ...]
```

---

# **New Part Compatibility**

When checking a **new, never-before-seen part**:

1. LLM extracts structured specs from text
2. Embedding for semantic comparison
3. Filtering by product assemblies
4. Compute compatibility score against all known parts
5. Return ranked results + explanations

This is a **digital twin–aware engineering recommender system**.

No PLM today does this.

---

# **FastAPI Backend**

API routes include:

* `/api/query` → RAG reasoning
* `/api/compat/product/{name}` → existing compatibility
* `/api/compat/new-part` → new part scoring
* `/api/upload/doc` → store BOMs/pdfs/images
* `/api/upload/yaml` → ingest new products
* `/api/stt` → Groq Whisper speech-to-text

Simple, clean, industry-ready.

---

# **React Frontend**

Key features:

* Dark text + white background “ERP style” UI
* RAG Query Mode
* Existing Compatibility Mode
* New Part Compatibility Mode
* Upload Documents
* YAML ingestion
* Download Markdown report

---

# Why this project is one-of-a-kind for Smart Manufacturing:

## **1. Combines PLM data + RAG + Graph Intelligence**

Manufacturing data is usually siloed in:

* PLM
* MES
* ERP
* Excel BOMs
* Vendor PDFs

This system unifies them into a **searchable digital thread**.

---

## **2. Compatible with real factory workflows**

Engineers frequently ask:

* “What part should I replace this with?”
* “Are these two components interchangeable?”
* “What does this assembly contain?”

No existing search engine can answer these without manual lookup.

This system can.

---

## **3. True engineering retrieval**

Most RAG systems are text-only.
This system uses:

### ✔ Graph context

✔ Specs
✔ Assemblies
✔ Vector embeddings
✔ Hierarchical similarity
✔ Multi-factor compatibility

This yields **far more accurate engineering answers**.

---

## **4. Novel compatibility scoring hybrid**

No manufacturing platform (PTC Windchill, Siemens Teamcenter, Dassault 3DEXPERIENCE) currently offers:

* ML-driven compatibility
* Assembly-aware matching
* LLM-based explanation of engineering alternatives

This system does.

---

## **5. Extensible digital thread**

Adding new machines/products is as easy as uploading a YAML file.

This makes it infinitely scalable across:

* entire factories
* robotics systems
* CNC fleets
* automotive component trees

---

## **6. AR "Explode View" Functionality**

This project also provides an AR extension to view the "explode view" of a machine, select the exact component, and review dependencies.

This extends its use-case into:

* internal dependency mapping
* predictive maintenance
* component vendor mapping
* intelligent product view

---

# 🚀 **Quick Start & Execution Guide**

Follow these step-by-step instructions to get the full digital thread application running locally on your system.

## **Prerequisites**
Before you begin, ensure you have the following installed:
* **Python 3.10+**: For backend APIs and ingestion.
* **Node.js (v18+) & npm**: For the Vite/React frontend dashboard.
* **Docker Desktop**: To spin up the Neo4j Graph Database.
* **Groq API Key**: Optional, but highly recommended for Graph-RAG synthesis and speech-to-text features.

---

## **Step 1: Clone and Set Up Environment**
1. Clone your repository and navigate to the project directory:
   ```bash
   cd asset-intelligence-graph-rag
   ```
2. Create your environment configuration file by copying the template or editing `.env` directly in your root directory:
   ```ini
   # Neo4j Settings
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=adwyteneo

   # Embedding Configuration (Uses 384-D gte-small by default)
   EMBEDDING_MODEL=thenlper/gte-small
   EMBEDDING_DIM=384

   # Groq LLM Settings (Required for Chat synthesis & Speech-To-Text)
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_CHAT_MODEL=llama-3.3-70b-versatile
   ```
   *(Note: The system has been upgraded to utilize the active `llama-3.3-70b-versatile` model instead of the decommissioned 3.1 model).*

---

## **Step 2: Spin Up the Neo4j Database**
We use Docker to run Neo4j with built-in APOC (Awesome Procedures on Cypher) plugins:
1. Start the container in detached mode:
   ```bash
   docker-compose up -d
   ```
2. Open your browser and navigate to the **Neo4j Browser Dashboard** at [http://localhost:7474](http://localhost:7474).
3. Connect using:
   * **Bolt URL**: `bolt://localhost:7687`
   * **Username**: `neo4j`
   * **Password**: `adwyteneo`

---

## **Step 3: Setup database constraints and indexes**
1. Copy the Cypher queries from the pre-configured [schema.cypher](cypher/schema.cypher) file.
2. Run them inside your Neo4j browser workspace command line to create the necessary unique constraints, indexes, and full-text vector spaces.
   
   > [!NOTE]
   > The schema is pre-optimized to use `IS UNIQUE` instead of the enterprise-only `IS NODE KEY` constraint, making it 100% compatible with both **Neo4j Community Edition** and Enterprise Edition out-of-the-box!

---

## **Step 4: Set Up and Ingest the Python Backend**
1. In the root directory, initialize and activate your Python virtual environment:
   ```powershell
   # Windows PowerShell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
2. Install all required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the ingestion scripts to load the sample products, component specifications, and embeddings into the Neo4j database:
   ```bash
   # A. Ingest Meta Quest 3 BOM
   python scripts/ingest.py --file examples/parts.yaml

   # B. Ingest 3D-Lathe BOM
   python scripts/ingest.py --file examples/3d-lathe.yaml

   # C. Ingest Industrial Lathe Machine BOM
   python scripts/ingest.py --file examples/modulathe.yaml
   ```
4. Precompute the component compatibility scores for each product:
   ```bash
   python scripts/compat.py --product "Meta Quest 3"
   python scripts/compat.py --product "3D-Lathe"
   python scripts/compat.py --product "Industrial Lathe Machine"
   ```
5. *(Optional)* Ingest additional documentation and generate version mappings for the Modulathe product:
   ```bash
   python examples/modulathe/ingest_modulathe_docs.py
   python examples/modulathe/compat_modulathe.py
   ```

---

## **Step 5: Launch the Servers**

### **A. Run the FastAPI Backend Server**
From your project root (with `.venv` activated), launch the backend using `uvicorn`:
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API is now running and documentable at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### **B. Run the React Frontend Dashboard**
1. Open a new terminal and navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install the web packages and start the Vite dev server:
   ```bash
   npm install
   npm run dev
   ```
3. Open [http://localhost:5173/](http://localhost:5173/) (or `http://localhost:5174/` if 5173 is occupied) to explore your stunning Asset Intelligence dashboard!

---

## **Alternative: Streamlit Prototyping Client**
If you prefer to run a single-process python dashboard instead of the full React app, you can launch the Streamlit variant:
```bash
streamlit run app/streamlit_app.py
```

---

# 🐳 **Running with Docker Compose (Production Stack)**

If you prefer to run the entire multi-container system (Neo4j Database + FastAPI Backend + React/Nginx Frontend) containerized under a single network mesh, you can use Docker Compose.

### **1. Spin Up the entire application stack**
In the root directory of your project, run:
```bash
docker compose up --build -d
```
*The `--build` flag ensures that your custom [backend/Dockerfile](backend/Dockerfile) and [frontend/Dockerfile](frontend/Dockerfile) are built into lightweight local images.*

### **2. Exposed Application Interfaces**
Once the services are running, the services map to the following ports on your localhost:
* 🌐 **React Frontend (Served by Nginx)**: [http://localhost:5173/](http://localhost:5173/)
* ⚙️ **FastAPI Backend (API Docs & Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
* 📊 **Neo4j Graph Dashboard**: [http://localhost:7474/](http://localhost:7474/)

### **3. Ingesting Data inside the Docker Container**
Since the containerized backend runs inside the container environment, you can trigger your initial database ingestions and precomputed compatibility mappings by sending exec commands directly into the active container:

```bash
# A. Ingest Product BOMs
docker exec -it graph-rag-backend python scripts/ingest.py --file examples/parts.yaml
docker exec -it graph-rag-backend python scripts/ingest.py --file examples/3d-lathe.yaml
docker exec -it graph-rag-backend python scripts/ingest.py --file examples/modulathe.yaml

# B. Precompute Component Compatibility
docker exec -it graph-rag-backend python scripts/compat.py --product "Meta Quest 3"
docker exec -it graph-rag-backend python scripts/compat.py --product "3D-Lathe"
docker exec -it graph-rag-backend python scripts/compat.py --product "Industrial Lathe Machine"

# C. Ingest Supplementary Docs & Mappings
docker exec -it graph-rag-backend python examples/modulathe/ingest_modulathe_docs.py
docker exec -it graph-rag-backend python examples/modulathe/compat_modulathe.py
```

### **4. Tear Down the Stack**
To stop all services and tear down the container stack cleanly, run:
```bash
docker compose down
```
