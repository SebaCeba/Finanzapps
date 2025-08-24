from decimal import Decimal, InvalidOperation
from .models import Dimension, Member

def parse_decimal_comma(s: str) -> Decimal | None:
    """
    Convierte string con separador decimal coma a Decimal.
    Ejemplos:
      '86,325'     -> Decimal('86.325')
      '1.234,56'   -> Decimal('1234.56')
    """
    if s is None:
        return None
    s = str(s).strip()
    s = s.replace('.', '')   # quita miles
    s = s.replace(',', '.')  # coma decimal -> punto
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        raise ValueError(f"monto inválido: {s}")

def get_member_id(dim_code: str, mem_code: str | None) -> int | None:
    """
    Busca members.id por dimension.code + member.code.
    Retorna None si mem_code es falsy.
    """
    if not mem_code:
        return None
    d = Dimension.query.filter_by(code=str(dim_code)).first()
    if not d:
        raise ValueError(f"dimension no existe: {dim_code}")
    m = Member.query.filter_by(dimension_id=d.id, code=str(mem_code)).first()
    if not m:
        raise ValueError(f"member no existe en {dim_code}: {mem_code}")
    return m.id
