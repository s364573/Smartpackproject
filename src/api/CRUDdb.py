# src/api/CRUDdb.py
from fastapi import APIRouter, HTTPException, Path, Response, status
from fastapi.openapi.models import Response
from pydantic import BaseModel, Field
from typing import List
import pandas as pd
from utils import bot_utils
import sql as sql_module

# Initialize connection
router = APIRouter()

chat_history = []
# Defined Pydantic models based on my TypeScript interfaces
class Kategori(BaseModel):
    kategoriid: int
    navn: str = Field(..., alias='kategorinavn')
    beskrivelse: str = Field(..., alias='kategoribeskrivelse')


class CreateKategori(BaseModel):
    kategorinavn: str
    kategoribeskrivelse: str


class UpdateKategori(BaseModel):
    kategorinavn: str
    kategoribeskrivelse: str


class Gjenstand(BaseModel):
    gjenstandid: int
    gjenstandnavn: str
    gjenstandbeskrivelse: str
    kategoriid: int


class CreateGjenstand(BaseModel):
    gjenstandnavn: str
    gjenstandbeskrivelse: str
    kategoriid: int


class UpdateGjenstand(BaseModel):
    gjenstandnavn: str
    gjenstandbeskrivelse: str
    kategoriid: int


class Regelverk(BaseModel):
    regelverkid: int
    kategoriid: int
    betingelse: str
    verdi: str
    tillatthandbagasje: bool
    tillattinnsjekketbagasje: bool
    regelverkbeskrivelse: str = Field(default="", alias='regelverkbeskrivelse')


class CreateRegelverk(BaseModel):
    kategoriid: int
    betingelse: str
    verdi: str
    tillatthandbagasje: bool
    tillattinnsjekketbagasje: bool
    regelverkbeskrivelse: str = Field(default="", alias='regelverkbeskrivelse')


class UpdateRegelverk(BaseModel):
    kategoriid: int
    betingelse: str
    verdi: str
    tillatthandbagasje: bool
    tillattinnsjekketbagasje: bool
    regelverkbeskrivelse: str = Field(default="", alias='regelverkbeskrivelse')


class RegelverkTag(BaseModel):
    regelverktagid: int
    gjenstandid: int
    regelverkid: int


class CreateRegelverkTag(BaseModel):
    gjenstandid: int
    regelverkid: int


class DeleteRegelverkTag(BaseModel):
    gjenstandid: int
    regelverkid: int


class DeleteRegelverkTagByItem(BaseModel):
    gjenstandid: int


@router.get("/")
async def all():
    return {"message": "Welcome to the SmartPack API!"}


@router.get("/query/{query}")
async def query(query: str):
    response = bot_utils.collection.query(
        query_texts=[query],  # Chroma will embed this
        n_results=5  # returns 5 results, change this if you want more or less
    )
    result_from_chroma = bot_utils.format_nicely(response)
    formatted_results_str = "\n\n".join(result_from_chroma)
    openai_result, user_input = bot_utils.openai_completion(query, formatted_results_str, chat_history)
    chat_history.append((user_input, openai_result.choices[0].message.content))  # Ensure it's a tuple

    return {"response": openai_result.choices[0].message.content}


# Kategorier
# CREATE
@router.post("/kategorier/", response_model=Kategori)
async def create_category(category: CreateKategori):
    query = """
    INSERT INTO kategorier (navn, beskrivelse)
    VALUES (%s, %s)
    RETURNING kategoriid, navn AS kategorinavn, beskrivelse AS kategoribeskrivelse;
    """
    values = (category.kategorinavn, category.kategoribeskrivelse)
    conn = sql_module.create_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")

    try:
        with conn.cursor() as cur:
            cur.execute(query, values)
            data = cur.fetchone()
            conn.commit()
            if not data:
                raise HTTPException(status_code=500, detail="Failed to create category")
            data_dict = dict(zip([desc[0] for desc in cur.description], data))
        return Kategori(**data_dict)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        conn.close()


# READ
@router.get("/kategorier/read/", response_model=List[Kategori])
async def get_categories():
    query = """
    SELECT kategoriid, navn AS kategorinavn, beskrivelse AS kategoribeskrivelse
    FROM kategorier
    ORDER BY navn;
    """
    conn = sql_module.create_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")

    try:
        result = sql_module.execute_query(conn, query)
        data = result.to_dict(orient='records')
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        conn.close()


@router.get("/kategorier/read/id/{kategoriid}", response_model=Kategori)
async def get_category(kategoriid: int):
    query = """
    SELECT kategoriid, navn AS kategorinavn, beskrivelse AS kategoribeskrivelse
    FROM kategorier
    WHERE kategoriid = %s;
    """
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        result = sql_module.execute_query(conn, query, (kategoriid,))
        if not result.empty:
            return Kategori(**result.iloc[0].to_dict())
        else:
            raise HTTPException(status_code=404, detail="Category not found")
    except Exception as e:
        print(f"Error while fetching category: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        conn.close()


# UPDATE
@router.put("/kategorier/update/{kategoriid}", response_model=Kategori)
async def update_category(kategoriid: int, category: UpdateKategori):
    query = """
    UPDATE kategorier
    SET navn = %s, beskrivelse = %s
    WHERE kategoriid = %s
    RETURNING kategoriid, navn AS kategorinavn, beskrivelse AS kategoribeskrivelse;
    """
    values = (category.kategorinavn, category.kategoribeskrivelse, kategoriid)
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        with conn.cursor() as cur:
            cur.execute(query, values)
            data = cur.fetchone()
            conn.commit()
            if data:
                data_dict = dict(zip([desc[0] for desc in cur.description], data))
                return Kategori(**data_dict)
            else:
                raise HTTPException(status_code=404, detail="Category not found")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        conn.close()


# DELETE Her er feil, sletter i databasen men feil uansett
@router.delete("/kategorier/delete/{kategoriid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(kategoriid: int):
    query = "DELETE FROM kategorier WHERE kategoriid = %s"
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (kategoriid,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Category not found")
            conn.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        conn.close()


# Gjenstander
# CREATE
@router.post("/gjenstander/", response_model=Gjenstand)
async def create_item(item: CreateGjenstand):
    query = """
    INSERT INTO gjenstander (gjenstandnavn, beskrivelse, kategoriid)
    VALUES (%s, %s, %s)
    RETURNING gjenstandid, gjenstandnavn, beskrivelse AS gjenstandbeskrivelse, kategoriid;
    """
    values = (item.gjenstandnavn, item.gjenstandbeskrivelse, item.kategoriid)
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchone()
            conn.commit()
            if result:
                data = dict(zip([desc[0] for desc in cursor.description], result))
                return Gjenstand(**data)
            else:
                raise HTTPException(status_code=404, detail="Failed to insert the item")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        conn.close()


# READ
# Leser alle gjenstander i orden av gjenstandnavn
@router.get("/gjenstander/read/", response_model=List[Gjenstand])
async def get_all_items():
    query = """
    SELECT gjenstandid, gjenstandnavn, beskrivelse AS gjenstandbeskrivelse, kategoriid
    FROM gjenstander
    ORDER BY gjenstandnavn;
    """
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        result = sql_module.execute_query(conn, query)
        data = result.to_dict(orient='records')
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# Les gjenstander basert på gjenstandid // Får feilmeldinger og burde bruke sqlalchemy
@router.get("/gjenstander/read/id/{gjenstandid}", response_model=Gjenstand)
async def get_item_by_id(gjenstandid: int):
    query = """
    SELECT gjenstandid, gjenstandnavn, beskrivelse AS gjenstandbeskrivelse, kategoriid
    FROM gjenstander
    WHERE gjenstandid = %s;
    """
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        result = pd.read_sql_query(query, conn, params=(gjenstandid,))
        if not result.empty:
            data = result.iloc[0].to_dict()
            return Gjenstand(**data)
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# Les gjenstander basert på gjenstandnavn
@router.get("/gjenstander/read/navn/{gjenstandnavn}", response_model=List[Gjenstand])
async def get_items_by_name(gjenstandnavn: str = Path(..., description="Navn på gjenstanden å søke etter")):
    query = """
    SELECT gjenstandid, gjenstandnavn, beskrivelse AS gjenstandbeskrivelse, kategoriid
    FROM gjenstander
    WHERE gjenstandnavn ILIKE %s
    ORDER BY gjenstandnavn;
    """
    like_pattern = f'%{gjenstandnavn}%'
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        with conn.cursor() as cur:
            cur.execute(query, (like_pattern,))
            rows = cur.fetchall()
            if rows:
                columns = [desc[0] for desc in cur.description]
                data = [dict(zip(columns, row)) for row in rows]
                return data
            else:
                raise HTTPException(status_code=404, detail="No items found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An SQL error occurred: {str(e)}")
    finally:
        conn.close()


# Les gjenstander baseert på kategoriid
@router.get("/gjenstander/read/kategori/{kategoriid}", response_model=List[Gjenstand])
async def get_items(kategoriid: int):
    query = """
    SELECT gjenstandid, gjenstandnavn, beskrivelse AS gjenstandbeskrivelse, kategoriid
    FROM gjenstander
    WHERE kategoriid = %s
    ORDER BY gjenstandnavn;
    """
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        result = sql_module.execute_query(conn, query, (kategoriid,))
        data = result.to_dict(orient='records')
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# UPDATE
@router.put("/gjenstander/update/{gjenstandid}", response_model=Gjenstand)
async def update_item(gjenstandid: int, item: UpdateGjenstand):
    query = """
    UPDATE gjenstander
    SET gjenstandnavn = %s, beskrivelse = %s, kategoriid = %s
    WHERE gjenstandid = %s
    RETURNING gjenstandid, gjenstandnavn, beskrivelse AS gjenstandbeskrivelse, kategoriid;
    """
    values = (item.gjenstandnavn, item.gjenstandbeskrivelse, item.kategoriid, gjenstandid)
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, values)
            conn.commit()
            result = cursor.fetchone()
            if result:
                data = dict(zip([desc[0] for desc in cursor.description], result))
                return Gjenstand(**data)
            else:
                raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        conn.close()


# DELETE Sletter men for feilmelding
@router.delete("/gjenstander/delete/{gjenstandid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(gjenstandid: int):
    query = "DELETE FROM gjenstander WHERE gjenstandid = %s"
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (gjenstandid,))
            if cursor.rowcount == 0:
                conn.rollback()
                raise HTTPException(status_code=404, detail="Item not found")
            conn.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        conn.close()


# Regelverker
# CREATE
@router.post("/regelverker/", response_model=Regelverk)
async def create_regelverk(regelverk: CreateRegelverk):
    query = """
    INSERT INTO regelverker (kategoriid, betingelse, verdi, tillatthandbagasje, tillattinnsjekketbagasje, beskrivelse)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING regelverkid, kategoriid, betingelse, verdi, tillatthandbagasje, tillattinnsjekketbagasje, beskrivelse;
    """
    values = (
        regelverk.kategoriid,
        regelverk.betingelse,
        regelverk.verdi,
        regelverk.tillatthandbagasje,
        regelverk.tillattinnsjekketbagasje,
        regelverk.regelverkbeskrivelse
    )
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, values)
            conn.commit()
            result = cursor.fetchone()
            if result:
                columns = [col[0] for col in cursor.description]
                data = dict(zip(columns, result))
                return Regelverk(**data)
            else:
                raise HTTPException(status_code=404, detail="Failed to insert regelverk")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        conn.close()


# READ
# Henter alle i rekkefølge av kategoriid
@router.get("/regelverker/read/", response_model=List[Regelverk])
async def get_regelverk():
    query = """
    SELECT 
        r.regelverkid, 
        r.kategoriid,  
        k.navn AS kategorinavn, 
        r.betingelse, 
        r.verdi, 
        r.tillatthandbagasje, 
        r.tillattinnsjekketbagasje, 
        COALESCE(r.beskrivelse, '') AS regelverkbeskrivelse
    FROM regelverker r
    INNER JOIN kategorier k ON r.kategoriid = k.kategoriid
    ORDER BY r.kategoriid;
    """
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        result = pd.read_sql_query(query, conn)
        if not result.empty:
            data = result.to_dict(orient='records')
            return data
        else:
            raise HTTPException(status_code=404, detail="No regelverk found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# Hent basert på regelverkID
@router.get("/regelverker/read/id/{regelverkid}", response_model=Regelverk)
async def get_regelverk_by_id(regelverkid: int):
    query = """
    SELECT regelverkid, kategoriid, betingelse, verdi, tillatthandbagasje, tillattinnsjekketbagasje, COALESCE(beskrivelse, '') AS regelverkbeskrivelse
    FROM regelverker
    WHERE regelverkid = %s;
    """
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (regelverkid,))
            data = cursor.fetchone()
            if data:
                columns = [col[0] for col in cursor.description]
                data_dict = dict(zip(columns, data))
                return Regelverk(**data_dict)
            else:
                raise HTTPException(status_code=404, detail="Regelverk not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        conn.close()


# Hent basert på kategoriID
@router.get("/regelverker/read/kategori/{kategoriid}", response_model=List[Regelverk])
async def get_regelverk_by_kategori(kategoriid: int):
    query = """
    SELECT regelverkid, kategoriid, betingelse, verdi, tillatthandbagasje, tillattinnsjekketbagasje, COALESCE(beskrivelse, '') AS regelverkbeskrivelse
    FROM regelverker
    WHERE kategoriid = %s
    ORDER BY kategoriid;
    """
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (kategoriid,))
            records = cursor.fetchall()
            data = [dict(zip([column[0] for column in cursor.description], row)) for row in records]
            if data:
                return data
            else:
                raise HTTPException(status_code=404, detail="No regelverk found for the specified category")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# UPDATE
@router.put("/regelverker/update/{regelverkid}", response_model=Regelverk)
async def update_regelverk(regelverkid: int, regelverk: UpdateRegelverk):
    query = """
    UPDATE regelverker
    SET betingelse = %s, verdi = %s, tillatthandbagasje = %s, tillattinnsjekketbagasje = %s, beskrivelse = %s
    WHERE regelverkid = %s
    RETURNING regelverkid, kategoriid, betingelse, verdi, tillatthandbagasje, tillattinnsjekketbagasje, beskrivelse;
    """
    values = (
        regelverk.betingelse,
        regelverk.verdi,
        regelverk.tillatthandbagasje,
        regelverk.tillattinnsjekketbagasje,
        regelverk.regelverkbeskrivelse,
        regelverkid
    )
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, values)
            conn.commit()
            data = cursor.fetchone()
            if data:
                columns = [col[0] for col in cursor.description]
                data_dict = dict(zip(columns, data))
                return Regelverk(**data_dict)
            else:
                raise HTTPException(status_code=404, detail="Regelverk not found")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# DELETE //Den sletter men kommer opp feilmelding
@router.delete("/regelverker/delete/{regelverkid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_regelverk(regelverkid: int = Path(..., description="The ID of the regelverk to delete")):
    query = "DELETE FROM regelverker WHERE regelverkid = %s"
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (regelverkid,))
            affected_rows = cursor.rowcount
            conn.commit()
            if affected_rows == 0:
                raise HTTPException(status_code=404, detail="Regelverk not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        conn.close()


# FOR å holde styr på gjenstander - regelverktag - regelverk
# Opprette koblinger mellom gjenstander og regelverk
@router.post("/regelverktag/", status_code=status.HTTP_201_CREATED, response_model=CreateRegelverkTag)
async def create_regelverktag(regelverktag: CreateRegelverkTag):
    query = """
    INSERT INTO regelverktag (gjenstandid, regelverkid)
    VALUES (%s, %s)
    RETURNING regelverktagid, gjenstandid, regelverkid;
    """
    values = (regelverktag.gjenstandid, regelverktag.regelverkid)
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, values)
            conn.commit()
            data = cursor.fetchone()
            if data:
                columns = [col[0] for col in cursor.description]
                data_dict = dict(zip(columns, data))
                return CreateRegelverkTag(**data_dict)
            else:
                raise HTTPException(status_code=404, detail="Failed to create regelverktag")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        conn.close()


# Slette koblinger mellom gjenstande rog regelverk    // Sletter men for feilmeldinger
@router.delete("/regelverktag/delete", status_code=status.HTTP_200_OK)
async def delete_regelverktag(regelverktag: DeleteRegelverkTag):
    query = """
    DELETE FROM regelverktag 
    WHERE gjenstandid = %s AND regelverkid = %s;
    """
    values = (regelverktag.gjenstandid, regelverktag.regelverkid)
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, values)
            conn.commit()
            return {"message": "RegelverkTag successfully deleted"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        conn.close()


# Sletter basert på gjenstandid alene.
@router.delete("/regelverktag/item/delete", status_code=status.HTTP_200_OK)
async def delete_regelverktag_by_item(regelverktag: DeleteRegelverkTagByItem):
    query = """
    DELETE FROM regelverktag 
    WHERE gjenstandid = %s;
    """
    values = (regelverktag.gjenstandid,)
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, values)
            conn.commit()
            return {"message": "RegelverkTag successfully deleted"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        conn.close()


# Sletter basert på gjenstandid alene.
@router.delete("/regelverktag/rule/delete", status_code=status.HTTP_200_OK)
async def delete_regelverktag_by_rule(regelverktag: DeleteRegelverkTagByItem):
    query = """
    DELETE FROM regelverktag 
    WHERE regelverkid = %s;
    """
    values = (regelverktag.gjenstandid,)
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, values)
            conn.commit()
            return {"message": "RegelverkTag successfully deleted"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        conn.close()


# Henter regelverker basert på gjenstandid
@router.get("/regelverker/read/{gjenstandid}", response_model=List[Regelverk])
async def get_rules(gjenstandid: int = Path(..., description="The ID of the item to fetch rules for")):
    query = """
    SELECT 
        reg.regelverkid, 
        reg.kategoriid,  
        reg.betingelse, 
        reg.verdi, 
        reg.tillatthandbagasje, 
        reg.tillattinnsjekketbagasje, 
        COALESCE(reg.beskrivelse, '') AS regelverkbeskrivelse
    FROM 
        regelverker reg
    INNER JOIN 
        regelverktag rtag ON reg.regelverkid = rtag.regelverkid
    WHERE 
        rtag.gjenstandid = %s
    ORDER BY 
        reg.regelverkid;
    """
    conn = sql_module.create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        data = sql_module.execute_query(conn, query, (gjenstandid,))
        if data.empty:
            raise HTTPException(status_code=404, detail="No rules found for this item")
        return data.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An SQL error occurred: {str(e)}")
    finally:
        conn.close()
