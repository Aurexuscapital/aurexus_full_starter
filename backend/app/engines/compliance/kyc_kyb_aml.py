from app.engines import register

def run(params: dict) -> dict:
    # Stub: pretend screening passed.
    return {"ok": True, "engine": "kyc_kyb_aml", "params": params, "status": "cleared"}

register(
    key="kyc_kyb_aml",
    fn=run,
    name="KYC/KYB/AML",
    description="Identity verification and AML screening."
)