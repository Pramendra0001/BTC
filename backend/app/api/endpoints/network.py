from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, IPEntity, ASNEntity
from app.schemas.schemas import IPEntityResponse, ASNEntityResponse

router = APIRouter()

from typing import List, Optional
from app.models.models import NetworkObservation, Transaction, TransactionInput, TransactionOutput

@router.get("/ips")
def list_ips(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total = db.query(IPEntity).count()
    ips = db.query(IPEntity).offset(skip).limit(limit).all()
    return {"ips": ips, "total": total}

@router.get("/ips/{ip}")
def get_ip(ip: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ip_ent = db.query(IPEntity).filter(IPEntity.ip_address == ip).first()
    if not ip_ent:
        raise HTTPException(status_code=404, detail="IP not found")
    
    observations = db.query(NetworkObservation).filter(NetworkObservation.src_ip == ip).order_by(NetworkObservation.timestamp.desc()).limit(50).all()
    txids = list(set(o.transaction_id for o in observations if o.transaction_id))
    
    related_wallets = set()
    if txids:
        txs = db.query(Transaction).filter(Transaction.txid.in_(txids)).all()
        tx_ids = [t.id for t in txs]
        if tx_ids:
            inputs = db.query(TransactionInput).filter(TransactionInput.transaction_id.in_(tx_ids)).all()
            outputs = db.query(TransactionOutput).filter(TransactionOutput.transaction_id.in_(tx_ids)).all()
            related_wallets.update(i.wallet_address for i in inputs if i.wallet_address)
            related_wallets.update(o.wallet_address for o in outputs if o.wallet_address)
            
    return {
        "ip_address": ip_ent.ip_address,
        "first_seen": ip_ent.first_seen.isoformat() if ip_ent.first_seen else None,
        "last_seen": ip_ent.last_seen.isoformat() if ip_ent.last_seen else None,
        "observation_count": ip_ent.observation_count,
        "asn": ip_ent.asn,
        "country": ip_ent.country,
        "recent_observations": [
            {
                "transaction_id": o.transaction_id,
                "dst_ip": o.dst_ip,
                "timestamp": o.timestamp.isoformat() if o.timestamp else None,
                "asn": o.asn,
                "geo_country": o.geo_country
            }
            for o in observations[:20]
        ],
        "related_txids": txids[:30],
        "related_wallets": list(related_wallets)[:30]
    }

@router.get("/asns")
def list_asns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total = db.query(ASNEntity).count()
    asns = db.query(ASNEntity).offset(skip).limit(limit).all()
    return {"asns": asns, "total": total}

@router.get("/asns/{asn}")
def get_asn(asn: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    asn_ent = db.query(ASNEntity).filter(ASNEntity.asn_number == asn).first()
    if not asn_ent:
        raise HTTPException(status_code=404, detail="ASN not found")
    
    ips = db.query(IPEntity).filter(IPEntity.asn == asn).limit(50).all()
    countries = db.query(NetworkObservation.geo_country).filter(
        NetworkObservation.asn == asn,
        NetworkObservation.geo_country.isnot(None)
    ).distinct().all()
    
    return {
        "asn_number": asn_ent.asn_number,
        "name": asn_ent.name,
        "country_count": asn_ent.country_count,
        "ip_count": asn_ent.ip_count,
        "associated_ips": [ip.ip_address for ip in ips],
        "associated_countries": [c[0] for c in countries if c[0]]
    }
