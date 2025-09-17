#!/usr/bin/env python3
import argparse, json, os, shutil, subprocess, sys, datetime, textwrap
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
ADV=os.path.join(ROOT,"ops","avances")
CK_DIR=os.path.join(ADV,"checkpoints")
INDEX=os.path.join(ADV,"index.jsonl")
TEMPLATE=os.path.join(ADV,"templates","TEMPLATE_CHECKPOINT.md")

def now():
    return datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")

def git(cmd):
    return subprocess.check_output(["git"]+cmd, cwd=ROOT, text=True).strip()

def changed_files():
    try:
        return git(["diff","--name-only"]).splitlines()
    except:
        return []

def write_context():
    # Construye CONTEXT_SESSION.md con el último checkpoint + resumen de cambios
    ctx=os.path.join(ADV,"CONTEXT_SESSION.md")
    last=None
    if os.path.exists(INDEX):
        *_,last=open(INDEX).read().splitlines() or [""]
    lines=[]
    lines.append("# CONTEXTO DE SESIÓN – MGComputacion\n")
    if last:
        item=json.loads(last)
        lines.append(f"**Último checkpoint:** {item.get('id')} — {item.get('title')}  \n")
        lines.append(f"**Fecha:** {item.get('ts')}  — **Tags:** {', '.join(item.get('tags',[]))}\n")
        lines.append(f"**Resumen:** {item.get('summary','')}\n")
    files=changed_files()
    if files:
        lines.append("\n## Cambios no comiteados\n")
        lines+= [f"- {f}" for f in files]
    with open(ctx,"w",encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(ctx)

def checkpoint(title, status="ESTABLE", tags=None, summary="", files=None):
    cid=f"{now()}_{title.lower().replace(' ','-')[:40]}"
    folder=os.path.join(CK_DIR,cid)
    os.makedirs(folder, exist_ok=True)
    if not files:
        files=changed_files()
    # Render simple del template
    with open(TEMPLATE,encoding="utf-8") as t:
        tpl=t.read()
    data={
        "title":title,"ts":datetime.datetime.utcnow().isoformat(timespec="seconds")+"Z",
        "author": os.getenv("USER","mgcom"), "status":status,
        "tags":", ".join(tags or []), "summary":summary or "(pendiente)",
        "changes":"(ver diff/git log)","files":"\n".join([f"- {x}" for x in files]) or "- (sin cambios)",
        "restore":"(ver documentación del servicio / backups)","notes":""
    }
    md=tpl
    for k,v in data.items():
        md=md.replace("{{"+k+"}}", str(v))
    mdfile=os.path.join(folder,"README.md")
    with open(mdfile,"w",encoding="utf-8") as f:
        f.write(md)
    # Guardar índice
    rec={"id":cid, "title":title, "ts":data["ts"], "status":status,
         "tags":tags or [], "summary":summary}
    with open(INDEX,"a",encoding="utf-8") as idx:
        idx.write(json.dumps(rec, ensure_ascii=False)+"\n")
    print(f"CREADO: {mdfile}")
    return cid

def list_ck(n=20):
    if not os.path.exists(INDEX): return
    with open(INDEX,encoding="utf-8") as f:
        for i,ln in enumerate(f.readlines()[-n:]):
            obj=json.loads(ln)
            print(f"{obj['ts']}  {obj['id']}  {obj['title']}  [{', '.join(obj.get('tags',[]))}]")

def show(cid):
    p=os.path.join(CK_DIR,cid,"README.md")
    print(open(p,encoding="utf-8").read())

def main():
    ap=argparse.ArgumentParser()
    sp=ap.add_subparsers(dest="cmd")

    sp.add_parser("context")
    pck=sp.add_parser("checkpoint")
    pck.add_argument("--title", required=True)
    pck.add_argument("--status", default="ESTABLE")
    pck.add_argument("--tags", nargs="*", default=[])
    pck.add_argument("--summary", default="")
    pck.add_argument("--files", nargs="*")

    p=sp.add_parser("list"); p.add_argument("-n",type=int,default=20)
    p=sp.add_parser("show"); p.add_argument("id")

    args=ap.parse_args()
    if args.cmd=="context": write_context()
    elif args.cmd=="checkpoint":
        checkpoint(args.title,args.status,args.tags,args.summary,args.files)
    elif args.cmd=="list": list_ck(args.n)
    elif args.cmd=="show": show(args.id)
    else: ap.print_help()

if __name__=="__main__":
    main()
