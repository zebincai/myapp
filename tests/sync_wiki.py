import os
import time
from typing import Any

import requests


BASE = "https://open.feishu.cn/open-apis"
TIMEOUT = 30

APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
SPACE_ID = os.getenv("FEISHU_WIKI_SPACE_ID")
ROOT_NODE = os.getenv("FEISHU_WIKI_NODE_TOKEN")


def require_env(name: str, value: str | None) -> str:
    if not value:
        raise RuntimeError(f"缺少环境变量：{name}")
    return value


def safe(res: requests.Response, action: str = "调用飞书接口") -> dict[str, Any]:
    try:
        payload = res.json()
    except ValueError as exc:
        raise RuntimeError(f"{action} 失败：HTTP {res.status_code}：{res.text[:200]}") from exc

    if res.status_code >= 400 or payload.get("code") != 0:
        raise RuntimeError(f"{action} 失败：HTTP {res.status_code}：{payload}")

    return payload


def get_token() -> str:
    url = f"{BASE}/auth/v3/tenant_access_token/internal"
    payload = safe(
        requests.post(
            url,
            json={
                "app_id": require_env("FEISHU_APP_ID", APP_ID),
                "app_secret": require_env("FEISHU_APP_SECRET", APP_SECRET),
            },
            timeout=TIMEOUT,
        ),
        "获取 tenant_access_token",
    )
    token = payload.get("tenant_access_token")
    if not token:
        raise RuntimeError(f"获取 tenant_access_token 失败：响应缺少 token：{payload}")
    return token


def create_doc(headers: dict[str, str], title: str) -> str:
    url = f"{BASE}/docx/v1/documents"
    payload = safe(
        requests.post(url, headers=headers, json={"title": title}, timeout=TIMEOUT),
        f"创建文档 {title}",
    )
    data = payload.get("data", {})
    doc_id = data.get("document_id") or data.get("document", {}).get("document_id")
    if not doc_id:
        raise RuntimeError(f"创建文档 {title} 失败：响应缺少 document_id：{payload}")
    return doc_id


def remove_readonly_fields(value: Any) -> Any:
    if isinstance(value, list):
        return [remove_readonly_fields(item) for item in value]
    if isinstance(value, dict):
        return {
            key: remove_readonly_fields(item)
            for key, item in value.items()
            if key != "merge_info"
        }
    return value


def convert_markdown(headers: dict[str, str], md: str) -> tuple[list[str], list[dict[str, Any]]]:
    if not md.strip():
        md = " "

    url = f"{BASE}/docx/v1/documents/blocks/convert"
    payload = safe(
        requests.post(
            url,
            headers=headers,
            params={"document_revision_id": -1},
            json={"content_type": "markdown", "content": md},
            timeout=TIMEOUT,
        ),
        "转换 Markdown 为文档块",
    )
    data = payload.get("data", {})
    first_level_ids = data.get("first_level_block_ids") or []
    blocks = data.get("blocks") or []

    if not first_level_ids or not blocks:
        raise RuntimeError(f"转换 Markdown 为文档块失败：响应缺少块数据：{payload}")

    return first_level_ids, remove_readonly_fields(blocks)


def write(headers: dict[str, str], doc_id: str, md: str) -> None:
    first_level_ids, blocks = convert_markdown(headers, md)
    if len(blocks) > 1000:
        raise RuntimeError(
            f"写入文档 {doc_id} 失败：转换后块数量为 {len(blocks)}，超过单次写入上限 1000"
        )

    url = f"{BASE}/docx/v1/documents/{doc_id}/blocks/{doc_id}/descendant"
    safe(
        requests.post(
            url,
            headers=headers,
            params={"document_revision_id": -1},
            json={
                "index": 0,
                "children_id": first_level_ids,
                "descendants": blocks,
            },
            timeout=TIMEOUT,
        ),
        f"写入文档 {doc_id}",
    )


def create_wiki_doc(headers: dict[str, str], parent_node: str, title: str) -> str:
    url = f"{BASE}/wiki/v2/spaces/{require_env('FEISHU_WIKI_SPACE_ID', SPACE_ID)}/nodes"
    payload = safe(
        requests.post(
            url,
            headers=headers,
            json={
                "obj_type": "docx",
                "parent_node_token": parent_node,
                "node_type": "origin",
                "title": title,
            },
            timeout=TIMEOUT,
        ),
        f"创建 Wiki 文档 {title}",
    )
    node = payload.get("data", {}).get("node", {})
    doc_id = node.get("obj_token")
    if not doc_id:
        raise RuntimeError(f"创建 Wiki 文档 {title} 失败：响应缺少 obj_token：{payload}")
    return doc_id


def list_matching_wiki_nodes(headers: dict[str, str], parent_node: str, title: str) -> list[dict[str, Any]]:
    url = f"{BASE}/wiki/v2/spaces/{require_env('FEISHU_WIKI_SPACE_ID', SPACE_ID)}/nodes"
    matches: list[dict[str, Any]] = []
    page_token = ""

    while True:
        params = {"parent_node_token": parent_node, "page_size": 50}
        if page_token:
            params["page_token"] = page_token

        payload = safe(
            requests.get(url, headers=headers, params=params, timeout=TIMEOUT),
            f"查找 Wiki 文档 {title}",
        )
        data = payload.get("data", {})
        matches.extend(
            node
            for node in data.get("items", [])
            if node.get("title") == title and node.get("obj_type") == "docx"
        )

        if not data.get("has_more"):
            break
        page_token = data.get("page_token") or data.get("next_page_token") or ""
        if not page_token:
            break

    return matches


def get_latest_wiki_doc(headers: dict[str, str], parent_node: str, title: str) -> str | None:
    matches = list_matching_wiki_nodes(headers, parent_node, title)
    if not matches:
        return None

    def create_time(node: dict[str, Any]) -> int:
        value = node.get("node_create_time") or node.get("obj_create_time") or 0
        return int(value)

    node = max(matches, key=create_time)
    if len(matches) > 1:
        print(f"发现 {len(matches)} 个同名 Wiki 文档，更新最新节点：{node.get('node_token')}")

    doc_id = node.get("obj_token")
    if not doc_id:
        raise RuntimeError(f"Wiki 文档 {title} 缺少 obj_token：{node}")
    return doc_id


def count_root_children(headers: dict[str, str], doc_id: str) -> int:
    url = f"{BASE}/docx/v1/documents/{doc_id}/blocks/{doc_id}/children"
    count = 0
    page_token = ""

    while True:
        params = {"document_revision_id": -1, "page_size": 500}
        if page_token:
            params["page_token"] = page_token

        payload = safe(
            requests.get(url, headers=headers, params=params, timeout=TIMEOUT),
            f"读取文档 {doc_id} 子块",
        )
        data = payload.get("data", {})
        count += len(data.get("items", []))

        if not data.get("has_more"):
            break
        page_token = data.get("page_token") or data.get("next_page_token") or ""
        if not page_token:
            break

    return count


def clear_doc(headers: dict[str, str], doc_id: str) -> None:
    child_count = count_root_children(headers, doc_id)
    if child_count == 0:
        return

    url = f"{BASE}/docx/v1/documents/{doc_id}/blocks/{doc_id}/children/batch_delete"
    safe(
        requests.delete(
            url,
            headers=headers,
            params={"document_revision_id": -1},
            json={"start_index": 0, "end_index": child_count},
            timeout=TIMEOUT,
        ),
        f"清空文档 {doc_id}",
    )
    time.sleep(1)


def get_or_create_wiki_doc(headers: dict[str, str], parent_node: str, title: str) -> str:
    doc_id = get_latest_wiki_doc(headers, parent_node, title)
    if doc_id:
        print(f"更新已有 Wiki 文档：{title}")
        clear_doc(headers, doc_id)
        return doc_id

    print(f"创建 Wiki 文档：{title}")
    return create_wiki_doc(headers, parent_node, title)


def sync_md(headers: dict[str, str], path: str, title: str, parent_node: str) -> None:
    print(f"同步文档：{title}")
    with open(path, "r", encoding="utf-8") as f:
        md = f.read()

    doc_id = get_or_create_wiki_doc(headers, parent_node, title)
    write(headers, doc_id, md)
    time.sleep(1)


def auto_grant_permission(headers: dict[str, str]) -> None:
    url = (
        f"{BASE}/wiki/v2/spaces/{require_env('FEISHU_WIKI_SPACE_ID', SPACE_ID)}"
        f"/nodes/{require_env('FEISHU_WIKI_NODE_TOKEN', ROOT_NODE)}/acl/members"
    )
    body = {
        "member_type": "app",
        "member_id": require_env("FEISHU_APP_ID", APP_ID),
        "perm": "full_access",
    }
    payload = safe(
        requests.post(url, headers=headers, json=body, timeout=TIMEOUT),
        "自动授权 Wiki 节点",
    )
    print("自动授权结果：", payload)


def main() -> None:
    print("开始同步")
    headers = {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json; charset=utf-8",
    }
    parent_node = require_env("FEISHU_WIKI_NODE_TOKEN", ROOT_NODE)
    docs_root = "./docs"
    failures = 0

    for root, _, files in os.walk(docs_root):
        for fname in sorted(files):
            if not fname.endswith(".md"):
                continue

            path = os.path.join(root, fname)
            rel_path = os.path.relpath(path, docs_root)
            title = os.path.splitext(rel_path)[0].replace(os.sep, " - ")

            try:
                sync_md(headers, path, title, parent_node)
            except RuntimeError as exc:
                failures += 1
                print(f"同步失败：{rel_path}：{exc}")

    if failures:
        print(f"同步完成，但有 {failures} 个文件失败")
        raise SystemExit(1)

    print("同步完成！")


if __name__ == "__main__":
    main()
