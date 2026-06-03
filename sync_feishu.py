import os, requests, time

APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
SPACE_ID = os.getenv("FEISHU_WIKI_SPACE_ID")
NODE_TOKEN = os.getenv("FEISHU_WIKI_NODE_TOKEN")

# 获取token
def get_tenant_token():
    res = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                        json={"app_id":APP_ID,"app_secret":APP_SECRET})
    return res.json()["tenant_access_token"]

token = get_tenant_token()
hdr = {"Authorization":f"Bearer {token}"}

# 遍历docs下所有md
md_dir = "./"
for f in os.listdir(md_dir):
    if f.endswith(".md"):
        file_path = os.path.join(md_dir,f)
        title = f[:-3]
        with open(file_path,"r",encoding="utf-8") as fp:
            content = fp.read()

        # 1.先创建云docx文档
        doc_create = requests.post("https://open.feishu.cn/open-apis/docx/v1/documents",hdr,json={"title":title})
        doc_id = doc_create.json()["data"]["document_id"]

        # 写入md内容
        requests.patch(f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks",hdr,json={
            "children":[{"type":"paragraph","paragraph":{"elements":[{"type":"markdown","markdown":{"content":content}}]}}]
        })

        # 挂载文档到Wiki节点
        requests.post("https://open.feishu.cn/open-apis/wiki/v2/spaces/{}/nodes/{}/documents".format(SPACE_ID,NODE_TOKEN),
                      hdr,json={"obj_type":"docx","obj_token":doc_id})
        print(f"✅ {f} 同步至Wiki成功")
        time.sleep(1)