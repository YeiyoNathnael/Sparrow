# 🏗️ System Architecture

## Overview

The Bus Route Optimization System is a full-stack application that uses machine learning and optimization algorithms to create efficient school bus routes. The system clusters students into zones based on residential proximity and destination similarity, then optimizes route sequences using reinforcement learning.

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    CLIENT LAYER                                          │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│   │                         React Frontend (Vite + TypeScript)                       │   │
│   │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐│   │
│   │  │  Dashboard   │ │   LiveMap    │ │  Operations  │ │  Optimization Studio     ││   │
│   │  │   Page       │ │    Page      │ │    Page      │ │       Page               ││   │
│   │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────────────┘│   │
│   │                                                                                  │   │
│   │  ┌─────────────────────────────────────────────────────────────────────────────┐│   │
│   │  │                         UI Components (shadcn/ui)                           ││   │
│   │  │   Cards • Charts (Recharts) • Forms • Dialogs • Buttons • Tables            ││   │
│   │  └─────────────────────────────────────────────────────────────────────────────┘│   │
│   │                                                                                  │   │
│   │  ┌─────────────────────────────────────────────────────────────────────────────┐│   │
│   │  │                      Map Visualization (Leaflet + React-Leaflet)            ││   │
│   │  │   Markers • Polylines • Routing Machine • Interactive Controls              ││   │
│   │  └─────────────────────────────────────────────────────────────────────────────┘│   │
│   └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                           │                                              │
│                                           │ HTTP/REST                                    │
│                                           ▼                                              │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                     API LAYER                                            │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│   │                           FastAPI Backend Server                                 │   │
│   │                                                                                  │   │
│   │   ┌────────────────────────────────────────────────────────────────────────┐    │   │
│   │   │                         REST API Endpoints                              │    │   │
│   │   │  GET /api/routes      GET /api/schools     GET /api/students           │    │   │
│   │   │  GET /api/routes/:id  GET /api/dashboard/metrics  GET /health          │    │   │
│   │   └────────────────────────────────────────────────────────────────────────┘    │   │
│   │                                                                                  │   │
│   │   ┌────────────────────────────────────────────────────────────────────────┐    │   │
│   │   │                         CORS Middleware                                 │    │   │
│   │   │            Allows cross-origin requests from frontend                   │    │   │
│   │   └────────────────────────────────────────────────────────────────────────┘    │   │
│   └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                           │                                              │
│                                           ▼                                              │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    DATA LAYER                                            │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│   │                              SQLite Database                                     │   │
│   │  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐                    │   │
│   │  │     routes      │ │     schools     │ │    students     │                    │   │
│   │  │ • id            │ │ • id            │ │ • id            │                    │   │
│   │  │ • route_number  │ │ • name          │ │ • school_id     │                    │   │
│   │  │ • school_names  │ │ • lat, lon      │ │ • assembly_point│                    │   │
│   │  │ • student_count │ │ • zone_id       │ │ • lat, lon      │                    │   │
│   │  │ • distance_km   │ └─────────────────┘ └─────────────────┘                    │   │
│   │  │ • polyline      │                                                            │   │
│   │  │ • optimization  │    ┌─────────────────────────────────────┐                 │   │
│   │  │   _score        │    │         JSON Data Files             │                 │   │
│   │  └─────────────────┘    │ • optimized_routes.json             │                 │   │
│   │                         │ • route_optimizer_input.json        │                 │   │
│   │                         │ • clustering_output.json            │                 │   │
│   │                         └─────────────────────────────────────┘                 │   │
│   └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               ML/OPTIMIZATION LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│   │                         Bus Pooling Clustering Pipeline                          │   │
│   │                                                                                  │   │
│   │   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │   │
│   │   │   Stage 1   │───▶│   Stage 2   │───▶│   Stage 3   │───▶│   Stage 4   │      │   │
│   │   │  Student    │    │    Zone     │    │   PyTorch   │    │    Route    │      │   │
│   │   │ Assignment  │    │  Clustering │    │ Optimizer   │    │  Optimizer  │      │   │
│   │   └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │   │
│   │         │                   │                  │                  │              │   │
│   │         ▼                   ▼                  ▼                  ▼              │   │
│   │   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │   │
│   │   │  Assign     │    │ Capacity-   │    │  Gumbel-    │    │  RL4CO      │      │   │
│   │   │  students   │    │ constrained │    │  Softmax    │    │  Attention  │      │   │
│   │   │  to nearest │    │  k-means    │    │  Soft       │    │  Model for  │      │   │
│   │   │  assembly   │    │  with       │    │  Clustering │    │  TSP        │      │   │
│   │   │  points     │    │  combined   │    │  + Gradient │    │  Solving    │      │   │
│   │   │             │    │  distance   │    │  Descent    │    │             │      │   │
│   │   └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │   │
│   └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.3.1 | UI component library |
| **TypeScript** | 5.8.3 | Type-safe JavaScript |
| **Vite** | 5.4.19 | Build tool & dev server |
| **TailwindCSS** | 3.4.17 | Utility-first CSS framework |
| **shadcn/ui** | - | Accessible UI components (Radix UI based) |
| **React Router** | 6.30.1 | Client-side routing |
| **TanStack Query** | 5.83.0 | Server state management |
| **Leaflet** | 1.9.4 | Interactive maps |
| **React-Leaflet** | 4.2.1 | React bindings for Leaflet |
| **Recharts** | 2.15.4 | Data visualization charts |
| **Lucide React** | 0.462.0 | Icon library |
| **Zod** | 3.25.76 | Schema validation |
| **React Hook Form** | 7.61.1 | Form management |

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | ≥0.104.0 | High-performance async API framework |
| **Uvicorn** | ≥0.24.0 | ASGI server |
| **SQLite** | - | Embedded relational database |
| **Python** | 3.11 | Backend runtime |

### ML/Optimization Engine

| Technology | Version | Purpose |
|------------|---------|---------|
| **PyTorch** | ≥2.0.0 | Deep learning framework |
| **NumPy** | ≥1.24.0 | Numerical computing |
| **SciPy** | ≥1.10.0 | Scientific computing |
| **RL4CO** | ≥0.4.0 | Reinforcement learning for combinatorial optimization |
| **PyTorch Geometric** | ≥2.3.0 | Graph neural networks |

### Infrastructure

| Technology | Purpose |
|------------|---------|
| **Render** | Cloud deployment platform |
| **Git/GitHub** | Version control |

---

## 🏛️ Architectural Decisions

### 1. **Monorepo Structure**

**Decision:** Keep frontend, backend, and ML engine in a single repository.

**Rationale:**
- Simplifies deployment coordination
- Easier local development
- Shared configuration and documentation
- Better suited for hackathon/small team context

### 2. **SQLite for Data Storage**

**Decision:** Use SQLite instead of PostgreSQL or other database servers.

**Rationale:**
- Zero configuration required
- Portable - database is a single file
- Sufficient for read-heavy workloads
- Reduces infrastructure complexity
- Can be easily migrated to PostgreSQL if scale demands

### 3. **FastAPI over Flask/Django**

**Decision:** Use FastAPI for the backend API.

**Rationale:**
- Native async support for better performance
- Automatic OpenAPI documentation
- Built-in request validation with Pydantic
- Modern Python type hints
- Excellent developer experience

### 4. **React + Vite over Next.js/CRA**

**Decision:** Use Vite with React instead of Next.js or Create React App.

**Rationale:**
- Lightning-fast HMR (Hot Module Replacement)
- No SSR complexity needed for this use case
- Simpler deployment as static files
- Modern ESM-first approach
- Better build performance

### 5. **Leaflet for Maps**

**Decision:** Use Leaflet instead of Google Maps or Mapbox.

**Rationale:**
- Free and open source
- No API key required for basic usage
- Excellent plugin ecosystem
- Good React integration via react-leaflet
- Lightweight and customizable

### 6. **RL4CO for Route Optimization**

**Decision:** Use Reinforcement Learning (RL4CO) for solving TSP/VRP instead of traditional solvers.

**Rationale:**
- State-of-the-art performance on combinatorial optimization
- GPU-accelerated for fast inference
- Learns generalizable policies
- No need for commercial solver licenses (vs. Gurobi/CPLEX)
- Research-backed implementation

### 7. **Two-Phase Route Optimization**

**Decision:** Separate pickup optimization from dropoff optimization.

**Rationale:**
- Ensures all pickups complete before dropoffs (realistic bus operation)
- Reduces problem complexity
- Allows for phase-specific optimization strategies
- More interpretable results

### 8. **Gumbel-Softmax for Differentiable Clustering**

**Decision:** Use Gumbel-Softmax trick for soft clustering optimization.

**Rationale:**
- Enables gradient-based refinement of cluster assignments
- Maintains differentiability for end-to-end training
- Can balance between soft and hard assignments via temperature
- Proven technique in neural combinatorial optimization

### 9. **Capacity-Constrained K-Means**

**Decision:** Custom k-means implementation with capacity constraints.

**Rationale:**
- Standard k-means doesn't respect capacity limits
- Essential for bus capacity constraints (20 students per bus)
- Combined distance metric (60% home, 40% school) for better clusters
- Handles multi-school bus pooling effectively

### 10. **Environment-Based API Configuration**

**Decision:** Use environment variables (`VITE_API_URL`) for API endpoints.

**Rationale:**
- Same codebase works in development and production
- No hardcoded URLs in source code
- Easy to switch backends for testing
- Standard 12-factor app practice

---

## 🔄 Data Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   CSV Files  │────▶│  Clustering  │────▶│   JSON       │
│  (Students,  │     │   Pipeline   │     │   Output     │
│   Schools,   │     │              │     │              │
│  Assembly    │     │   PyTorch +  │     │ clustering_  │
│   Points)    │     │    RL4CO     │     │ output.json  │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │◀────│   FastAPI    │◀────│   SQLite     │
│   React UI   │     │   Backend    │     │   Database   │
│              │     │              │     │              │
│  Dashboard   │     │  /api/routes │     │   routes     │
│  LiveMap     │     │  /api/schools│     │   schools    │
│  Operations  │     │  /api/students     │   students   │
└──────────────┘     └──────────────┘     └──────────────┘
```

---

## 📁 Project Structure

```
nate/
├── frontend/                    # React frontend application
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   │   ├── ui/              # shadcn/ui components
│   │   │   ├── layout/          # Layout components (Sidebar, TopNav)
│   │   │   ├── map/             # Map-specific components
│   │   │   └── dialogs/         # Dialog components
│   │   ├── pages/               # Route pages
│   │   │   ├── Dashboard.tsx    # Metrics overview
│   │   │   ├── LiveMap.tsx      # Route visualization
│   │   │   ├── Operations.tsx   # Route management
│   │   │   └── Settings.tsx     # Configuration
│   │   ├── config/              # Configuration files
│   │   │   └── api.ts           # API endpoint config
│   │   ├── hooks/               # Custom React hooks
│   │   ├── services/            # API services
│   │   └── types/               # TypeScript types
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                     # FastAPI backend
│   ├── main.py                  # API server & endpoints
│   ├── requirements.txt
│   └── nexus.db                 # SQLite database (generated)
│
├── src/                         # ML/Optimization engine
│   ├── clustering_pipeline.py   # Main orchestration
│   ├── models/
│   │   ├── student_assignment.py    # Student → Assembly point
│   │   ├── zone_clustering.py       # Assembly → Bus zones
│   │   ├── pytorch_optimizer.py     # Gradient-based refinement
│   │   ├── route_optimizer.py       # RL4CO route optimization
│   │   └── output.py                # Output formatting
│   └── utils/
│       ├── data_structures.py       # Core data classes
│       ├── distance.py              # Haversine calculations
│       └── metrics.py               # Quality metrics
│
├── data/                        # Sample data files
├── config/                      # Configuration files
├── render.yaml                  # Render deployment config
├── requirements.txt             # Python dependencies (ML engine)
└── README.md
```

---

## 🚀 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Render Cloud                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌────────────────────────────────────────────────────┐    │
│   │              Backend Web Service                    │    │
│   │         bus-route-optimizer-api                     │    │
│   │                                                     │    │
│   │   • Python 3.11 Runtime                             │    │
│   │   • FastAPI + Uvicorn                               │    │
│   │   • Auto-deploy on push                             │    │
│   │   • Health check: /health                           │    │
│   │                                                     │    │
│   │   URL: https://bus-route-optimizer-api.onrender.com │    │
│   └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Frontend (Static Hosting Options)               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Options:                                                   │
│   • Vercel (recommended for Vite)                            │
│   • Netlify                                                  │
│   • Render Static Site                                       │
│   • GitHub Pages                                             │
│                                                              │
│   Environment Variable:                                      │
│   VITE_API_URL=https://bus-route-optimizer-api.onrender.com │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Security Considerations

1. **CORS Configuration**: Currently allows all origins (`*`) for development. Should be restricted to specific domains in production.

2. **Input Validation**: FastAPI provides automatic request validation via Pydantic models.

3. **Database**: SQLite file should be excluded from version control (`.gitignore`) when containing real data.

4. **Environment Variables**: Sensitive configuration stored in environment variables, not code.

---

## 📈 Scalability Considerations

| Component | Current | Scaling Path |
|-----------|---------|--------------|
| Database | SQLite (single file) | PostgreSQL on Render |
| API | Single Uvicorn worker | Multiple workers + load balancer |
| ML Engine | CPU-based | GPU instances for RL4CO |
| Frontend | Static files | CDN distribution |

---

## 🧪 Testing Strategy

- **Frontend**: Vitest + React Testing Library
- **Backend**: FastAPI TestClient + pytest
- **ML Engine**: pytest + synthetic data validation

---

## 📚 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [RL4CO Paper & Docs](https://github.com/ai4co/rl4co)
- [Leaflet Documentation](https://leafletjs.com/)
- [shadcn/ui Components](https://ui.shadcn.com/)
