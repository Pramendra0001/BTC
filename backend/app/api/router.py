from fastapi import APIRouter
from app.api.endpoints import (
    health, auth, dashboard, search, datasets, alerts, wallets, transactions,
    network, graph, timeline, evidence, cases, models, ai, processing,
    heuristics, data_quality, audit, users, jobs
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(wallets.router, prefix="/wallets", tags=["Wallets"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(network.router, prefix="", tags=["Network"]) # Has /ips and /asns inside
api_router.include_router(graph.router, prefix="/graph", tags=["Graph"])
api_router.include_router(timeline.router, prefix="/timeline", tags=["Timeline"])
api_router.include_router(evidence.router, prefix="/evidence", tags=["Evidence"])
api_router.include_router(cases.router, prefix="/cases", tags=["Cases"])
api_router.include_router(models.router, prefix="/models", tags=["Models"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
api_router.include_router(processing.router, prefix="/processing", tags=["Processing"])
api_router.include_router(heuristics.router, prefix="/heuristics", tags=["Heuristics"])
api_router.include_router(data_quality.router, prefix="/data-quality", tags=["Data Quality"])
api_router.include_router(audit.router, prefix="/audit-logs", tags=["Audit Logs"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
