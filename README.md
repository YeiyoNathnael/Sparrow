# Sparrow

Sparrow plans school bus routes for students attending different schools in the same area. It groups students into shared bus zones, orders each bus's stops with a neural combinatorial optimization model, and presents the routes in a map dashboard.

The project was built by team The Embassy for the Bounty Challenge hackathon hosted by the Google Developers Club at the University of Birmingham Dubai.

## Features

- Assigns students to their nearest assembly points
- Groups assembly points into capacity-limited bus zones, with up to three schools per zone
- Refines zones with differentiable soft clustering in PyTorch
- Orders stops with the POMO model from RL4CO
- Serves routes, schools, students and metrics through a REST API
- Shows routes on an interactive map with a dashboard and optimization controls
- Exports results as JSON and GeoJSON

## Pipeline

```text
Student, school and assembly point CSVs
                 |
   Stage 1: Student assignment
                 |
   Stage 2: Zone clustering
                 |
   Stage 3: PyTorch refinement
                 |
   Stage 4: Route optimization
                 |
         SQLite and REST API
                 |
          React dashboard
```

### Stage 1: Student assignment

Each student is assigned to the nearest assembly point using batched Haversine distances computed in PyTorch.

### Stage 2: Zone clustering

Assembly points are grouped using capacity-constrained k-means with k-means++ initialization. The distance metric weights home proximity at 0.6 and school proximity at 0.4.

### Stage 3: PyTorch refinement

A differentiable clustering model uses Gumbel-Softmax assignments and the Adam optimizer. Its loss function combines distance, capacity, balance and compactness terms.

### Stage 4: Route optimization

Each route is solved in two phases, pickups followed by drop-offs. Coordinates are normalized and passed to an RL4CO attention model that uses POMO decoding, and the resulting tour is mapped back to the stop sequence.

## Getting started

### Requirements

- Python 3.11
- Node.js 20 or later

### Run the pipeline

```bash
pip install -r requirements.txt
python run_pipeline.py
```

| Option | Description |
|---|---|
| `--cluster-only` | Runs clustering only |
| `--optimize-only` | Runs route optimization only |
| `--preset <name>` | Uses a preset dataset from `config/datasets.yaml` |

### Run the backend

```bash
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --port 8000
```

### Run the frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

The dashboard runs at `http://localhost:8080` and connects to the API at `VITE_API_URL`.

## API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health |
| `GET` | `/api/routes` | All routes. Accepts `peak_hours=true` |
| `GET` | `/api/routes/{route_id}` | A single route |
| `GET` | `/api/schools` | All schools |
| `GET` | `/api/students` | All students |
| `GET` | `/api/dashboard/metrics` | Dashboard metrics |

## Configuration

Datasets and their map centers are set in `config/datasets.yaml`. The expected CSV formats are described in [`data/README.md`](data/README.md).

| Parameter | Default | Description |
|---|---|---|
| `bus_capacity` | 20 | Maximum students per bus |
| `max_schools_per_zone` | 3 | Maximum schools served by one bus |
| `school_proximity_threshold` | 5.0 km | Maximum distance between schools in a zone |
| `home_weight` | 0.6 | Weight of residential proximity |
| `school_weight` | 0.4 | Weight of school proximity |
| `max_walking_distance` | 2.0 km | Maximum walk to an assembly point |
| `use_pytorch_optimization` | True | Enables the refinement stage |
| `optimization_epochs` | 100 | Refinement iterations |

## Metrics

The pipeline reports silhouette score, intra-cluster and inter-cluster distances, walking distances, capacity utilization, and schools per zone.

## Project layout

```text
backend/                 FastAPI service and SQLite database
config/                  Dataset configuration
data/                    Example datasets and CSV format reference
docs/                    Backend and frontend documentation
frontend/                React dashboard
src/
  clustering_pipeline.py Pipeline entry point
  models/
    student_assignment.py
    zone_clustering.py
    pytorch_optimizer.py
    route_optimizer.py
    output.py
  utils/                 Distance functions, data structures and metrics
run_pipeline.py          Runs the full pipeline
ARCHITECTURE.md          System architecture
USAGE.md                 Usage guide
```

## Built with

- Machine learning: PyTorch, RL4CO, PyTorch Geometric
- Backend: Python, FastAPI, SQLite
- Frontend: React, TypeScript, Vite, Tailwind CSS, shadcn/ui, Leaflet, Recharts

## Authors

- Nathnael Workneh Yeiyo
