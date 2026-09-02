from typing import List

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Header,
)

import os
import shutil

from backend.app.services.pdf_service import (
    extract_text_from_pdf
)

from backend.app.services.docx_service import (
    extract_text_from_docx
)

from backend.app.services.txt_service import (
    extract_text_from_txt
)

from backend.app.services.image_service import (
    extract_text_from_image
)

from backend.app.utils.chunking import (
    chunk_text
)

from backend.app.services.embedding_service import (
    create_embeddings
)

from backend.app.services.chroma_service import (
    store_chunks
)

from backend.app.core.config import UPLOAD_DIR

router = APIRouter()


@router.post("/upload")
async def upload_files(
        files: List[UploadFile] = File(...),
        x_session_id: str = Header(default="default"),
):

    # UPGRADED: each session's raw files live in their own subfolder, so
    # two different sessions uploading "resume.pdf" never overwrite each
    # other on disk (previously they shared one flat folder).
    session_upload_dir = os.path.join(UPLOAD_DIR, x_session_id)
    os.makedirs(session_upload_dir, exist_ok=True)

    uploaded_files = []

    for file in files:

        file_path = f"{session_upload_dir}/{file.filename}"

        with open(
                file_path,
                "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        if file.filename.lower().endswith(
                ".pdf"
        ):

            text = extract_text_from_pdf(
                file_path
            )

        elif file.filename.lower().endswith(
                ".docx"
        ):

            text = extract_text_from_docx(
                file_path
            )

        elif file.filename.lower().endswith(
                ".txt"
        ):

            text = extract_text_from_txt(
                file_path
            )

        elif file.filename.lower().endswith(
                (
                    ".png",
                    ".jpg",
                    ".jpeg"
                )
        ):

            text = extract_text_from_image(
                file_path
            )

        else:

            continue

        chunks = chunk_text(
            text
        )

        embeddings = create_embeddings(
            chunks
        )

        store_chunks(
            chunks,
            embeddings,
            file.filename,
            x_session_id,
        )

        uploaded_files.append(
            {
                "document":
                    file.filename,

                "chunks":
                    len(chunks)
            }
        )

    return {
        "message":
            "Files stored in ChromaDB",

        "documents":
            uploaded_files
    }
