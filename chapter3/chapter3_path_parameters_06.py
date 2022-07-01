from fastapi import FastAPI, Path


app = FastAPI()
LICENSE_REGEX = r"^\w{2}-\d{3}-\w{2}$"


@app.get("/license-plates/{license}")
async def get_license_plate(license: str = Path(..., regex=LICENSE_REGEX)):
    return {"license": license}
