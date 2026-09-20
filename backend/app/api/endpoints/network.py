from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, IPEntity, ASNEntity
from app.schemas.schemas import IPEntityResponse, ASNEntityResponse

router = APIRouter()

@router.get("/ips/{ip}", response_model=IPEntityResponse)
def get_ip(ip: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ip_ent = db.query(IPEntity).filter(IPEntity.ip_address == ip).first()
    if not ip_ent:
        raise HTTPException(status_code=404, detail="IP not found")
    return ip_ent

@router.get("/asns/{asn}", response_model=ASNEntityResponse)
def get_asn(asn: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    asn_ent = db.query(ASNEntity).filter(ASNEntity.asn_number == asn).first()
    if not asn_ent:
        raise HTTPException(status_code=404, detail="ASN not found")
    return asn_ent
