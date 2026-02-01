# Data Directory

Place your CSV files here and update `config/datasets.yaml` to point to them.

## Required CSV Files

### 1. `students.csv`

Student residential locations.

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `student_id` | string | ✓ | Unique student identifier |
| `lat` | float | ✓ | Home latitude (e.g., 25.0934) |
| `lon` | float | ✓ | Home longitude (e.g., 55.2341) |
| `name` | string | | Student name |
| `grade` | string | | Grade level |
| `phone` | string | | Contact number |

**Example:**
```csv
student_id,lat,lon,name,grade
STU001,25.0934,55.2341,Ahmed Al-Maktoum,Grade 5
STU002,25.1012,55.2289,Fatima Hassan,Grade 3
STU003,25.0867,55.2401,Mohammed Ali,Grade 7
```

---

### 2. `schools.csv`

School locations and information.

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `school_id` | string | ✓ | Unique school identifier |
| `latitude` | float | ✓ | School latitude |
| `longitude` | float | ✓ | School longitude |
| `school_name` | string | ✓ | School name |
| `capacity` | int | | Maximum student capacity |
| `address` | string | | Full address |

**Example:**
```csv
school_id,latitude,longitude,school_name,capacity,address
SCH001,25.0934,55.2341,Kings School Al Barsha,1500,Al Barsha 2
SCH002,25.1012,55.2289,GEMS Wellington,2000,Al Sufouh
SCH003,25.0867,55.2401,Dubai British School,1200,Emirates Hills
```

---

### 3. `associations.csv`

Links students to their schools.

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `student_id` | string | ✓ | Student ID (must exist in students.csv) |
| `school_id` | string | ✓ | School ID (must exist in schools.csv) |

**Example:**
```csv
student_id,school_id
STU001,SCH001
STU002,SCH002
STU003,SCH001
```

---

### 4. `assembly_points.csv`

Bus pickup/collection points where students gather.

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `stop_id` | string | ✓ | Unique stop identifier |
| `lat` | float | ✓ | Stop latitude |
| `lon` | float | ✓ | Stop longitude |
| `name` | string | | Stop name/description |
| `capacity` | int | | Maximum students at this stop |

**Example:**
```csv
stop_id,lat,lon,name,capacity
STOP001,25.0950,55.2200,Al Barsha Mall Entrance,30
STOP002,25.1000,55.2250,MOE Metro Station,50
STOP003,25.0900,55.2150,Park Gate A,25
```

---

## Coordinate System

All coordinates must be in **WGS84 (GPS coordinates)**:
- Latitude: -90 to 90 (positive = North)
- Longitude: -180 to 180 (positive = East)

For Dubai:
- Latitude: ~25.0 (North)
- Longitude: ~55.2 (East)

---

## Setting Up Your Data

1. **Create your CSV files** following the format above

2. **Place them in this directory** (or anywhere accessible):
   ```
   data/
   ├── students.csv
   ├── schools.csv
   ├── associations.csv
   └── assembly_points.csv
   ```

3. **Update the config file** (`config/datasets.yaml`):
   ```yaml
   active_dataset:
     name: "My Custom Dataset"
     students_csv: "data/students.csv"
     schools_csv: "data/schools.csv"
     associations_csv: "data/associations.csv"
     assembly_points_csv: "data/assembly_points.csv"
     map_center:
       latitude: 25.0950
       longitude: 55.2200
     region: "Your Region Name"
   ```

4. **Run the pipeline**:
   ```bash
   python run_pipeline.py
   ```

---

## Tips

- **Unique IDs**: Make sure all IDs are unique within their file
- **Matching IDs**: Student IDs in associations.csv must exist in students.csv
- **No missing coords**: Every row must have valid lat/lon values
- **UTF-8 encoding**: Save files as UTF-8 to support international characters
- **No BOM**: Some editors add a BOM; use "UTF-8 without BOM" if available

---

## Validating Your Data

Run validation without processing:
```bash
python run_pipeline.py --validate
```

This checks that all required CSV files exist and are readable.
