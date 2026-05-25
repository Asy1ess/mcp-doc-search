# MCP 호스트 연동 설정

**Claude Desktop**, **Cursor**, 또는 **둘 다** 연동할 수 있습니다.  
사용하는 앱에 맞는 예시만 복사해 적용하면 됩니다.

공통 조건:

- Docker Desktop 실행 중
- 프로젝트에서 `docker compose build` 완료
- `Documents\test` 등 대상 폴더 **색인 완료** (`src.indexer.cli`)

## 경로 수정

예시의 `COMPOSE_FILE`를 본인 PC의 `docker-compose.yml` **절대 경로**로 바꿉니다.

```
C:\Users\user1\mcp-doc-search\docker-compose.yml
```

---

## A. Claude Desktop만

1. `%APPDATA%\Claude\claude_desktop_config.json` 열기 (없으면 생성)
2. [`claude_desktop_config.example.json`](claude_desktop_config.example.json) 내용을 붙여 넣거나 `mcpServers` 항목만 병합
3. Claude Desktop **완전 종료 후 재실행**

## B. Cursor만

1. `C:\Users\<사용자>\.cursor\mcp.json` 열기
2. [`cursor-mcp.example.json`](cursor-mcp.example.json)의 `mcp-doc-search` 블록을 기존 `mcpServers`에 **추가**
3. Cursor **재시작** 또는 MCP 설정 새로고침

## C. 둘 다 사용

- A + B를 각각 적용
- 같은 `data/` 색인을 공유하므로 **한 번 색인**하면 두 앱 모두 검색 가능
- `reindex`는 **한쪽에서만** 실행 권장

---

## 동작 확인

채팅에서 예시 질의:

> 보안 관련 문서 찾아줘

도구 `search_documents`, `get_document_content`, `list_indexed_folders`, `reindex` 가 보이면 성공입니다.
