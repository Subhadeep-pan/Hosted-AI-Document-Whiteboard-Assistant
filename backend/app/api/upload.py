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

    # Each session has its own folder.
    session_upload_dir = os.path.join(
        UPLOAD_DIR,
        x_session_id
    )

    os.makedirs(
        session_upload_dir,
        exist_ok=True
    )

    uploaded_files = []

    for file in files:

        file_path = os.path.join(
            session_upload_dir,
            file.filename
        )

        # Save uploaded file
        with open(
                file_path,
                "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        # Extract text based on file type
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

        # Split extracted text into chunks
        chunks = chunk_text(
            text
        )

        total_chunks = len(chunks)

        # Process chunks in small batches.
        # This prevents all embeddings from staying
        # in RAM at the same time.
        batch_size = 16

        for i in range(
                0,
                total_chunks,
                batch_size
        ):

            batch_chunks = chunks[
                i:i + batch_size
            ]

            # Create embeddings only for this batch
            embeddings = create_embeddings(
                batch_chunks
            )

            # Store this batch immediately
            store_chunks(
                batch_chunks,
                embeddings,
                file.filename,
                x_session_id,
            )

            # Release temporary memory
            del embeddings
            del batch_chunks

        uploaded_files.append(
            {
                "document":
                    file.filename,

                "chunks":
                    total_chunks
            }
        )

        # Release extracted text and chunks
        del text
        del chunks

    return {
        "message":
            "Files stored in ChromaDB",

        "documents":
            uploaded_files
    }