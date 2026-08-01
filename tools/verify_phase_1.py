#!/usr/bin/env python3
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
required=['compose.yaml','.env.example','services/control-plane-java/pom.xml','analytics/queueforge-python/pyproject.toml','engines/simulation-cpp/CMakeLists.txt','apps/web/package.json','apps/web/package-lock.json','apps/web/src/App.tsx','.github/workflows/quality.yml','contracts/schemas/worker-health.schema.json']
missing=[x for x in required if not (root/x).is_file()]
if missing: raise SystemExit('Missing Phase 1 files: '+', '.join(missing))
for x in ['apps/web/package.json','apps/web/package-lock.json','contracts/schemas/worker-health.schema.json']: json.load(open(root/x))
print(f'Phase 1 repository verification passed ({len(required)} key files).')
