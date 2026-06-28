# 🌐 Worker Event-Driven - Template

Este repositorio contiene un **worker desacoplado** basado en eventos que consume mensajes desde Pub/Sub (emulado o GCP real), interactúa con storage (MinIO/GCS) y persiste resultados en base de datos.

Está pensado como **template base para construir workers reales**, siguiendo buenas prácticas de:
- procesamiento asíncrono
- persistencia de jobs
- control de errores
- observabilidad

---

## 📦 Estructura del proyecto

```
worker_system/
├── config/
│ └── settings.py              # Variables de entorno
├── core/
│ ├── database.py             # Conexión DB (Local / Cloud SQL)
│ └── logger.py               # Logger
├── db/
│ ├── base.py                 # Base de SQLAlchemy
│ └── database_tables.py      # Nombres de tablas
├── integrations/
│ ├── pubsub.py               # Cliente Pub/Sub
│ └── storage.py              # Cliente Storage (MinIO/GCS)
├── shared/
│ ├── base_worker.py          # Clase base del worker
│ └── utils.py
└── workers/
    └── example/
        ├── job.py            # Lógica del job
        ├── main.py           # Entry point
        └── model.py          # Modelo DB del job
```

---

## ⚙️ Configuración

Se utiliza `.env.localdev` para entorno local.

### 🔹 Generales

```
PROJECT_NAME=event-worker-template
ENVIRONMENT_NAME=LOCALDEV
LOG_LEVEL=DEBUG
```

### 🔹 Pub/Sub

```
GCP_PROJECT_ID=poc-realidad-alterada
PUBSUB_EMULATOR_HOST=http://pubsub-emulator:8085
EXAMPLE_SUBSCRIPTION_ID=example-sub
```

### 🔹 Storage

```
STORAGE_PROVIDER=minio
STORAGE_BUCKET=my-bucket
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=password123
MINIO_SECURE=False
```

### 🔹 Database

```
DATABASE_URL=postgresql+asyncpg://admin:password@db:5432/app_db
DATABASE_SCHEMA=workspace
```

---

## 🚀 Ejecución

Desde el workspace principal:

```
docker compose up worker-example
```

El worker se conecta automáticamente a:
- Pub/Sub Emulator
- MinIO
- PostgreSQL

---

## 🧠 Flujo del Worker

1. Se cargan variables (`settings`)
2. Se inicializan dependencias:
   - DB
   - Storage
3. Se inicia el `BaseWorker`
4. El worker:
   - Espera la subscription
   - Escucha mensajes
   - Ejecuta el job
   - Maneja errores
   - Hace ACK automático

---

## 🔄 Flujo REAL de procesamiento

```
Backend → Pub/Sub → Worker → DB + Storage
```

### Paso a paso:

1. Backend sube archivos a storage
2. Backend publica mensaje:

```json
{
  "folder_id": "uuid",
  "files": ["path/file1.jpg", "path/file2.png"]
}
```

3. Worker recibe mensaje
4. Worker:

- crea registro en DB (`WorkerJob`)
- procesa archivos
- guarda resultado
- marca status (`done` o `failed`)
- hace ACK

---

## 🧠 Persistencia de Jobs (IMPORTANTE)

Cada procesamiento queda registrado en DB:

Tabla: `worker_jobs`

Campos clave:

- `status`: pending | processing | done | failed
- `payload`: mensaje original
- `result`: resultado del procesamiento
- `error`: error si falló

👉 Esto permite:
- debug real
- trazabilidad
- evitar "trabajos fantasma"
- auditoría

---

## 📝 Ejemplo de Job

Archivo: `workers/example/job.py`

```python
async def run_example_job(payload: dict, storage):
    # 1. Crear job en DB
    # 2. Procesar archivos (descarga desde MinIO)
    # 3. Validar contenido
    # 4. Guardar resultado
    # 5. Actualizar status
```

---

## ⚠️ Manejo de errores y ACK

### 🔴 Si el job falla:

- NO se hace ACK
- Pub/Sub reintenta automáticamente

### 🟢 Si el job termina:

- Se hace ACK
- El mensaje se elimina de la cola

---

## 🚨 Riesgo importante

Si haces ACK aunque falle:

❌ pierdes el mensaje  
❌ pierdes el trabajo  
❌ no hay retry  

Por eso:

👉 **El ACK solo debe ocurrir si el procesamiento terminó correctamente**

---

## 🔁 Reintentos (Retry)

En GCP puedes configurar:

- máximo de intentos
- backoff
- dead-letter queue

En local:
- los retries son automáticos e infinitos (emulador)

---

## 🧵 Concurrencia (Queue control)

El worker procesa mensajes en loop.

Opciones para controlar carga:

### 1. Serial (default)
1 mensaje a la vez

### 2. Paralelo controlado (ejemplo futuro)

```python
semaphore = asyncio.Semaphore(3)
```

👉 limita a 3 jobs concurrentes

---

## 🛠 BaseWorker

Centraliza inicialización:

```python
async def setup():
    await init_db()
    await storage.start()
```

👉 Permite que nuevos workers:
- no repitan código
- solo definan su job

---

## 🧪 Desarrollo

### Cambios en código

No necesitas rebuild:

```
docker compose restart worker-example
```

Gracias a:

```
volumes:
  - ./workers:/app
```

---

## 🧱 Docker

```
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY src ./src

RUN pip install --upgrade pip \
 && pip install .

ENV PYTHONPATH=/app

CMD ["sh", "-c", "python ${WORKER_PATH}"]
```

---

## 🧠 Buenas prácticas

✔ Persistir TODO en DB  
✔ Nunca confiar solo en logs  
✔ No hacer ACK en fallos  
✔ Mantener jobs idempotentes  
✔ Separar infraestructura de lógica  

---

## 🔮 Futuro

- Dead Letter Queue
- Retry policies avanzadas
- Workers paralelos
- Observabilidad (metrics + tracing)
- Orquestación por tipo de job

---

## 💡 Nota importante de arquitectura

Este worker **duplica modelos del backend intencionalmente**.

👉 Esto permite:
- desacoplamiento real
- independencia de deploy
- evitar dependencias cruzadas

⚠️ Trade-off:
- mantenimiento manual (copy-paste de modelos)

---

## 🧪 Estado actual

✔ Worker funcionando  
✔ DB integrada  
✔ Storage integrado  
✔ Pub/Sub integrado  
✔ Flujo completo probado end-to-end  

---

🚀 Listo para escalar a producción