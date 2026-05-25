# MCP Doc Search

PC에 저장된 문서를 **파일명이 완전히 일치하지 않아도** 의미적으로 검색할 수 있는 MCP(Model Context Protocol) 서버입니다.  
Claude Desktop 등 MCP 호스트에서 자연어로 질의하면, 로컬 문서를 벡터 유사도 검색으로 찾아줍니다.

> 예: "작년 예산안 관련 문서 찾아줘" → 파일명에 '예산'이 없어도 내용이 유사한 PDF·Word·Excel 등을 반환

**Repository:** https://github.com/Asy1ess/mcp-doc-search

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| **의미 검색** | 질의와 문서 내용의 의미적 유사도 기반 검색 (ChromaDB + 임베딩) |
| **다양한 포맷 지원** | PDF, DOCX, XLSX, PPTX, TXT, HWPX |
| **문서 단위 결과** | 청크 단위 검색 후 파일 단위로 집계·순위화 |
| **MCP 도구 제공** | Claude Desktop 등에서 바로 호출 가능 |
| **증분 색인** *(확장)* | 파일 변경 감지 후 변경분만 재색인 |

---

## 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│  MCP Host (Claude Desktop 등)                           │
└────────────────────────┬────────────────────────────────┘
                         │ stdio
┌────────────────────────▼────────────────────────────────┐
│  MCP Server Layer (FastMCP)                             │
│  search_documents · get_document_content                │
│  list_indexed_folders · reindex                         │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Search Engine                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ Crawler  │→ │ Extractor│→ │ Chunker  │→ │ Embedder│ │
│  └──────────┘  └──────────┘  └──────────┘  └────┬────┘ │
│                                                    │      │
│  ┌──────────┐                              ┌──────▼────┐ │
│  │ SQLite   │  (파일 메타·해시·색인 상태)   │ ChromaDB  │ │
│  └──────────┘                              └───────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 디렉터리 구조

```
mcp-doc-search/
├── src/
│   ├── mcp_server/       # FastMCP 서버 · 도구 정의
│   ├── crawler/          # 폴더 순회 · 파일 필터링
│   ├── extractors/       # 포맷별 텍스트 추출기
│   ├── chunker/          # 텍스트 분할
│   ├── embedder/         # 임베딩 생성
│   ├── indexer/          # 색인 파이프라인
│   └── search/           # 유사도 검색 · 결과 집계
├── tests/
├── data/                 # ChromaDB · SQLite (gitignore)
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── requirements.txt
└── README.md
```

---

## 기술 스택

| 영역 | 선택 | 비고 |
|------|------|------|
| 언어 | Python 3.10+ | Docker 이미지: 3.11-slim |
| 실행 환경 | Docker Compose | 개발·실행 환경 통일 |
| MCP | [FastMCP](https://github.com/jlowin/fastmcp) | stdio 전송 |
| 벡터 DB | ChromaDB | 로컬 영구 저장 |
| 메타 DB | SQLite | 파일 경로·해시·색인 시각 |
| 임베딩 | `bge-m3` (로컬) 또는 외부 API | `.env`로 전환 |
| 키워드 검색 *(확장)* | Kiwi + BM25 + RRF | 하이브리드 검색 |

---

## MCP 도구

| 도구 | 설명 |
|------|------|
| `search_documents` | 자연어 질의로 유사 문서 검색 (스니펫 포함) |
| `get_document_content` | 특정 파일의 전체 또는 일부 텍스트 반환 |
| `list_indexed_folders` | 현재 색인된 폴더 목록 |
| `reindex` | 지정 폴더 전체 또는 증분 재색인 |

---

## 설치

### 요구 사항

- [Docker](https://www.docker.com/) 및 Docker Compose v2
- (로컬 임베딩 사용 시) 충분한 RAM — `bge-m3` 기준 약 2GB+

로컬 Python venv 없이 **Docker Compose**로 실행 환경을 맞춥니다.

### 1. 저장소 클론

```bash
git clone https://github.com/Asy1ess/mcp-doc-search.git
cd mcp-doc-search
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
```

`.env`에서 `DOCUMENTS_PATH`를 PC의 문서 폴더 경로로 수정합니다.

```env
DOCUMENTS_PATH=C:\Users\you\Documents
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=BAAI/bge-m3
CHROMA_PERSIST_DIR=/app/data/chroma
SQLITE_PATH=/app/data/index.db
INDEX_FOLDERS=/documents
CHUNK_SIZE=800
CHUNK_OVERLAP=100
```

### 3. 이미지 빌드 및 컨테이너 기동

코드를 수정·`git pull` 한 뒤에는 **반드시 이미지를 다시 빌드**하세요. 예전 이미지를 쓰면 `extracted` 로그만 나오고 검색 CLI가 없을 수 있습니다.

```bash
docker compose build
docker compose up -d
```

빌드 반영 확인:

```bash
docker compose run --rm app ls src/search/cli.py
```

`No module named src.search.cli` 가 나오면 → `docker compose build` 가 안 된 상태입니다.

개발용 셸이 필요하면:

```bash
docker compose --profile dev run --rm dev
```

### 4. 초기 색인

첫 실행 시 **bge-m3 모델 다운로드**로 시간이 걸릴 수 있습니다. 같은 파일은 해시가 같으면 건너뜁니다.

```bash
docker compose build
docker compose run --rm app python -m src.indexer.cli --folder /documents/test -v
```

### 4-1. 의미 검색 테스트

```bash
docker compose run --rm app python -m src.search.cli "예산 관련 문서"
```

### 5. MCP 호스트 연동 (Claude Desktop / Cursor)

**둘 중 하나만 써도 되고, 둘 다 써도 됩니다.** 같은 Docker 이미지·같은 `data/` 색인을 공유합니다.

| 사용 환경 | 설정 파일 | 예시 |
|-----------|-----------|------|
| Claude Desktop만 | `%APPDATA%\Claude\claude_desktop_config.json` | [`config/claude_desktop_config.example.json`](config/claude_desktop_config.example.json) |
| Cursor만 | `~/.cursor/mcp.json` | [`config/cursor-mcp.example.json`](config/cursor-mcp.example.json) |
| Cursor + Notion 등 기존 MCP | 위 `mcp.json`에 블록 **추가** | [`config/cursor-mcp-with-notion.example.json`](config/cursor-mcp-with-notion.example.json) |

자세한 병합 방법: [`config/README.md`](config/README.md)

공통 설정 (경로는 본인 PC에 맞게 수정):

```json
"mcp-doc-search": {
  "command": "docker",
  "args": [
    "compose",
    "-f",
    "C:\\Users\\user1\\mcp-doc-search\\docker-compose.yml",
    "run",
    "--rm",
    "-T",
    "app"
  ]
}
```

- `-T`: stdio 연결용 (TTY 비활성화)
- 호스트 앱 **재시작** 후 도구 목록에 `search_documents` 등이 보이는지 확인

예시 질의:

> "보안 관련 문서 찾아줘"

### 테스트

```bash
docker compose run --rm app pytest tests/ -q
```

### 로컬 venv (선택)

Docker 없이 디버깅할 때만 사용합니다.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest tests/ -q
```

---

## 지원 파일 형식

| 확장자 | 상태 | 추출 방식 |
|--------|------|-----------|
| `.pdf` | MVP | pdfplumber / PyMuPDF |
| `.docx` | MVP | python-docx |
| `.xlsx` | MVP | openpyxl |
| `.pptx` | MVP | python-pptx |
| `.txt`, `.md` | MVP | chardet (EUC-KR 등 자동 감지) |
| `.hwpx` | MVP | XML 파싱 |
| `.hwp` | 확장 | LibreOffice headless 변환 |
| 스캔 PDF | 확장 | OCR (Tesseract 등) |

---

## 개발 로드맵

| 단계 | 내용 | 상태 |
|------|------|------|
| 0 | 프로젝트 기반 설정 (Git, Docker Compose, `.env`) | 완료 |
| 1 | 색인 엔진 (수집 → 추출 → 청킹 → 임베딩) | 완료 |
| 2 | 의미 검색 | 완료 |
| 3 | MCP 서버 레이어 | 예정 |
| 4 | Claude Desktop / Cursor MCP 연동 | 설정 예시 완료 (각자 적용) |
| 5 | 하이브리드 검색 · 증분 색인 · 안정성 | 확장 |
| 6 | 테스트 · 문서화 | 예정 |

**MVP 완료 기준:** 지정 폴더 색인 → Claude Desktop에서 자연어 검색 → 관련 파일·스니펫 반환

---

## 알려진 한계 (예정)

- 암호가 걸린 문서는 건너뜀
- 대용량 파일·이미지 위주 문서는 텍스트 추출 품질이 낮을 수 있음
- 초기 색인은 문서 수·용량에 따라 시간 소요
- HWP(구형)는 LibreOffice 설치 필요

---

## 라이선스

MIT — [LICENSE](LICENSE)

---

## 관련 링크

- [Notion 프로젝트 페이지](https://www.notion.so/daca16fb0fc4423e94d7531431314498) — 기능별 To-do 및 일정
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)
