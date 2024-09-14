# controllers.py
from fastapi import APIRouter, HTTPException, Depends, Body, Security
from typing import List
from models import Terrtories, load_data_from_google_sheets, get_current_time,get_api_key,get_google_sheets_credentials, get_db_pool
import aiomysql

router = APIRouter()

@router.post("/addUGCReport")
async def add_entry(
    UGC_id: str = Body(...),
    poster_territory_id: str = Body(...),
    reporter_territory_id: str = Body(...),
    knowledge_id: str = Body(...),
    Url: str = Body(...),
    Problem_Description: str = Body(...),
    api_key: str = Depends(get_api_key)
):
    try:
        sheet_id = "1rIcrh0unYHwh3ufuj79Xfj_KPJTxgU_xid-_wnEFBOs"
        sheet_name = "Sheet1"
        
        credentials = get_google_sheets_credentials()
        gc = pygsheets.authorize(custom_credentials=credentials)
        sh = gc.open_by_key(sheet_id)
        worksheet = sh.worksheet_by_title(sheet_name)

        current_time = get_current_time('Asia/Kolkata')

        worksheet.append_table([
            UGC_id,
            poster_territory_id,
            reporter_territory_id,
            knowledge_id,
            Url,
            Problem_Description,
            current_time
        ])

        return {"status": "success", "message": "Entry added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/getDistinctTerritories")
async def get_distinct_territories(
    req: Terrtories,
    api_key: str = Depends(get_api_key)
):
    sheet_name = req.sheet_name
    area = req.area

    if not sheet_name or not area:
        raise HTTPException(status_code=400, detail="Sheet name and area are required")

    try:
        data = load_data_from_google_sheets(sheet_name)

        if not data:
            raise HTTPException(status_code=404, detail="No data found in the sheet")

        headers = data[0].keys()
        Area_key = 'Area'
        Territories_key = "Territory"
        if Area_key not in headers or Territories_key not in headers:
            raise HTTPException(status_code=400, detail="Area column not found in the sheet")
        
        territories_list = {row[Territories_key] for row in data if row[Area_key] == area}

        if not territories_list:
            raise HTTPException(status_code=404, detail="No data found in the sheet")

        return list(territories_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while fetching data from the sheet")

@router.post("/postVisitGuide")
async def post_visit_guide(
    territory_id: str = Body(...),
    store_name: str = Body(...),
    partner: str = Body(...),
    api_key: str = Depends(get_api_key)
):
    current_time = get_current_time('America/Los_Angeles')

    if not store_name or not partner or not territory_id:
        raise HTTPException(status_code=400, detail="Missing required parameters")

    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = "INSERT INTO VisitGuideMetadata (territory_id, store_name, partner, timestamp) VALUES (%s, %s, %s, %s)"
                await cursor.execute(query, (territory_id, store_name, partner, current_time))
                await conn.commit()
                return {"message": "Visit guide metadata inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
