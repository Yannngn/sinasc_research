from data.loader import data_loader


# Geographic utility functions
def get_region_from_id_code(id_code: str) -> str:
    """
    Get geographic region from state code.

    Args:
        id_code: One-digit, two-digit, six or seven-digit code (e.g., "1", "11", "1100015", "3550308")

    Returns:
        Region name (Norte, Nordeste, Sudeste, Sul, Centro-Oeste)
    """
    if not id_code or len(str(id_code)) < 1:
        return "Desconhecido"

    first_digit = str(id_code)[0]
    regions = {
        "1": "Norte",
        "2": "Nordeste",
        "3": "Sudeste",
        "4": "Sul",
        "5": "Centro-Oeste",
    }
    return regions.get(first_digit, "Desconhecido")


def get_state_from_id_code(id_code: str) -> str:
    """
    Get geographic state from state code.

    Args:
        id_code: Two-digit, six or seven-digit code (e.g., "11", "1100015", "3550308")

    Returns:
        Region name (Norte, Nordeste, Sudeste, Sul, Centro-Oeste)
    """
    if not id_code or len(str(id_code)) < 2:
        return "Desconhecido"

    first_digits = str(id_code)[:1]
    # Normalize to two-digit IBGE state code (e.g., 11, 35)
    code = str(id_code).zfill(2)
    first_digits = code[:2]

    states = data_loader._load_state_mapping()
    return states.get(first_digits, "Desconhecido")


def get_municipality_from_id_code(id_code: str) -> str:
    """
    Get geographic municipality name from municipality IBGE code.

    Args:
        id_code: Six or seven-digit code (e.g., "1100015", "3550308", or numeric)

    Returns:
        Municipality name or "Desconhecido" if not found
    """
    if not id_code:
        return "Desconhecido"

    code_str = str(id_code).strip()

    # Require at least 6 digits to attempt lookup (keep original behavior)
    if len(code_str) < 6:
        return "Desconhecido"

    # Normalize to 6-digit IBGE municipality code (take last 6 digits if longer)
    first_digits = str(id_code)[:6]
    code_norm = first_digits.zfill(6)

    mapping = data_loader._load_municipality_mapping()
    return mapping.get(code_norm, "Desconhecido")
