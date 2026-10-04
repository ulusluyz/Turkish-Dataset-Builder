import uuid
import json
import csv
from typing import Iterator, Optional, Dict, Any
from dataset_cleaner.ingestion.schema import RawDocument
from dataset_cleaner.ingestion.json_utils import extract_text_from_dict

def read_txt(filepath: str) -> Iterator[RawDocument]:
    """Reads TXT/MD files using robust fallback encoding detection."""
    encodings = ["utf-8", "utf-8-sig", "windows-1254", "iso-8859-9", "latin-1"]
    content = None
    used_enc = "utf-8"
    for enc in encodings:
        try:
            with open(filepath, "r", encoding=enc) as f:
                content = f.read()
                used_enc = enc
                break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if content is None:
        with open(filepath, "rb") as f:
            raw = f.read()
            content = raw.decode("utf-8", errors="replace")
            used_enc = "utf-8-replace"

    doc_id = str(uuid.uuid4())
    yield RawDocument(
        doc_id=doc_id,
        source_file=filepath,
        text=content,
        metadata={"encoding_used": used_enc}
    )

def read_jsonl(filepath: str, text_field: Optional[str] = None) -> Iterator[RawDocument]:
    """Streams JSONL line by line."""
    line_num = 0
    encodings = ["utf-8", "utf-8-sig", "windows-1254", "latin-1"]

    # Try opening file
    f = None
    for enc in encodings:
        try:
            f = open(filepath, "r", encoding=enc)
            # test read line
            f.readline()
            f.seek(0)
            break
        except Exception:
            f = None
            continue

    if f is None:
        f = open(filepath, "r", encoding="utf-8", errors="replace")

    with f:
        for line in f:
            line_num += 1
            line_str = line.strip()
            if not line_str:
                continue
            try:
                data = json.loads(line_str)
                if isinstance(data, dict):
                    text, field_used = extract_text_from_dict(data, text_field)
                    if text:
                        yield RawDocument(
                            doc_id=str(uuid.uuid4()),
                            source_file=filepath,
                            text=text,
                            metadata={"original_json": data},
                            line_number=line_num,
                            field_used=field_used
                        )
                elif isinstance(data, str):
                    yield RawDocument(
                        doc_id=str(uuid.uuid4()),
                        source_file=filepath,
                        text=data,
                        line_number=line_num
                    )
            except Exception:
                continue

def read_json(filepath: str, text_field: Optional[str] = None) -> Iterator[RawDocument]:
    """Reads JSON array or object document."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)

        if isinstance(data, list):
            for idx, item in enumerate(data):
                if isinstance(item, dict):
                    text, field_used = extract_text_from_dict(item, text_field)
                    if text:
                        yield RawDocument(
                            doc_id=str(uuid.uuid4()),
                            source_file=filepath,
                            text=text,
                            metadata={"original_json": item},
                            line_number=idx + 1,
                            field_used=field_used
                        )
                elif isinstance(item, str):
                    yield RawDocument(
                        doc_id=str(uuid.uuid4()),
                        source_file=filepath,
                        text=item,
                        line_number=idx + 1
                    )
        elif isinstance(data, dict):
            text, field_used = extract_text_from_dict(data, text_field)
            if text:
                yield RawDocument(
                    doc_id=str(uuid.uuid4()),
                    source_file=filepath,
                    text=text,
                    metadata={"original_json": data},
                    field_used=field_used
                )
    except Exception:
        pass

def read_csv_tsv(filepath: str, is_tsv: bool = False, text_field: Optional[str] = None) -> Iterator[RawDocument]:
    """Streams CSV / TSV rows."""
    delimiter = "\t" if is_tsv else ","
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row_idx, row in enumerate(reader):
                text, field_used = extract_text_from_dict(row, text_field)
                if text:
                    yield RawDocument(
                        doc_id=str(uuid.uuid4()),
                        source_file=filepath,
                        text=text,
                        metadata={"original_row": row},
                        line_number=row_idx + 1,
                        field_used=field_used
                    )
    except Exception:
        pass

def read_pdf(filepath: str) -> Iterator[RawDocument]:
    """Reads PDF document using pypdf if available."""
    try:
        import pypdf
        reader = pypdf.PdfReader(filepath)
        text_parts = []
        for i, page in enumerate(reader.pages):
            txt = page.extract_text()
            if txt:
                text_parts.append(txt)
        full_text = "\n\n".join(text_parts).strip()
        if full_text:
            yield RawDocument(
                doc_id=str(uuid.uuid4()),
                source_file=filepath,
                text=full_text,
                metadata={"pdf_pages": len(reader.pages), "pdf_extracted": True}
            )
        else:
            yield RawDocument(
                doc_id=str(uuid.uuid4()),
                source_file=filepath,
                text="",
                metadata={"pdf_pages": len(reader.pages), "pdf_extracted": False, "scanned_or_empty": True}
            )
    except Exception as e:
        yield RawDocument(
            doc_id=str(uuid.uuid4()),
            source_file=filepath,
            text="",
            metadata={"pdf_error": str(e)}
        )

def read_document_stream(filepath: str, file_type: str, text_field: Optional[str] = None) -> Iterator[RawDocument]:
    """Dispatcher streaming reader based on file_type."""
    if file_type in ("txt", "markdown", "html", "xml", "yaml"):
        yield from read_txt(filepath)
    elif file_type == "jsonl":
        yield from read_jsonl(filepath, text_field=text_field)
    elif file_type == "json":
        yield from read_json(filepath, text_field=text_field)
    elif file_type == "csv":
        yield from read_csv_tsv(filepath, is_tsv=False, text_field=text_field)
    elif file_type == "tsv":
        yield from read_csv_tsv(filepath, is_tsv=True, text_field=text_field)
    elif file_type == "pdf":
        yield from read_pdf(filepath)
