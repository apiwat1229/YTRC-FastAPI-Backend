import os
import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency, get_current_user
from app.schemas.knowledge_book import CreateKnowledgeBookDto, UpdateKnowledgeBookDto
from app.services.knowledge_books_service import KnowledgeBooksService

router = APIRouter(prefix="/knowledge-books", tags=["Knowledge Books"])


@router.post("/upload", dependencies=[Depends(get_current_user)])
async def upload_book(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form(...),
    description: str | None = Form(None),
    author: str | None = Form(None),
    tags: str | None = Form(None),
    trainingDate: str | None = Form(None),
    attendees: int | None = Form(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file uploaded")

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type: Only PDF files are allowed"
        )

    upload_dir = Path("uploads/knowledge-books")
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = os.path.splitext(file.filename)[1] if file.filename else ".pdf"
    filename = f"{secrets.token_hex(16)}{ext}"
    file_path = upload_dir / filename

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    tags_list = []
    if tags:
        try:
            import json

            tags_list = json.loads(tags)
        except Exception:
            tags_list = [t.strip() for t in tags.split(",") if t.strip()]

    payload = CreateKnowledgeBookDto(
        title=title,
        description=description,
        category=category,
        fileType="pdf",
        fileName=file.filename or filename,
        filePath=str(file_path),
        fileSize=len(content),
        author=author,
        tags=tags_list,
        uploadedBy=current_user["userId"],
        trainingDate=trainingDate,
        attendees=attendees or 0,
    )

    return await KnowledgeBooksService(db).create(payload)


@router.get("", dependencies=[Depends(get_current_user)])
async def find_all_books(
    category: str | None = None,
    search: str | None = None,
    tags: str | None = None,
    uploadedBy: str | None = None,
    db: AsyncSession = Depends(db_session_dependency),
):
    filters = {
        "category": category,
        "search": search,
        "tags": tags.split(",") if tags else None,
        "uploadedBy": uploadedBy,
        "isPublished": True,
    }
    return await KnowledgeBooksService(db).find_all(filters)


@router.get("/categories", dependencies=[Depends(get_current_user)])
async def get_categories(db: AsyncSession = Depends(db_session_dependency)):
    return await KnowledgeBooksService(db).get_categories()


@router.get("/stats", dependencies=[Depends(get_current_user)])
async def get_stats(db: AsyncSession = Depends(db_session_dependency)):
    return await KnowledgeBooksService(db).get_stats()


@router.get("/{book_id}", dependencies=[Depends(get_current_user)])
async def find_one_book(book_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await KnowledgeBooksService(db).find_one(book_id)


@router.get("/{book_id}/file", dependencies=[Depends(get_current_user)])
async def get_file(book_id: str, db: AsyncSession = Depends(db_session_dependency)):
    book = await KnowledgeBooksService(db).find_one(book_id)
    file_path = Path(book["filePath"])

    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    return FileResponse(
        path=str(file_path.absolute()),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{book["fileName"]}"'},
    )


@router.get("/{book_id}/download", dependencies=[Depends(get_current_user)])
async def download_file(book_id: str, db: AsyncSession = Depends(db_session_dependency)):
    service = KnowledgeBooksService(db)
    book = await service.find_one(book_id)
    await service.increment_download(book_id)

    file_path = Path(book["filePath"])
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    return FileResponse(
        path=str(file_path.absolute()),
        media_type="application/pdf",
        filename=book["fileName"],
    )


@router.post("/{book_id}/view", dependencies=[Depends(get_current_user)])
async def track_view(
    book_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    await KnowledgeBooksService(db).track_view(book_id, current_user["userId"])
    return {"message": "View tracked successfully"}


@router.patch("/{book_id}", dependencies=[Depends(get_current_user)])
async def update_book(
    book_id: str,
    payload: UpdateKnowledgeBookDto,
    db: AsyncSession = Depends(db_session_dependency),
):
    return await KnowledgeBooksService(db).update(book_id, payload)


@router.delete("/{book_id}", dependencies=[Depends(get_current_user)])
async def delete_book(book_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await KnowledgeBooksService(db).remove(book_id)
