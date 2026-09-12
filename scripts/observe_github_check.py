"""Read real GitHub run/check identity. Metadata alone never admits an experience."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, pathlib, re, shutil, subprocess

def collect(repository, commit, run_id, check_id, api):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repository) or '..' in repository:
        raise ValueError('Invalid public repository identifier')
    if not re.fullmatch(r'[0-9a-f]{40}',commit) or not str(run_id).isdigit() or not str(check_id).isdigit():
        raise ValueError('Exact commit, numeric run and check IDs required')
    repo=api(f'repos/{repository}')
    if repo.get('private') is not False or repo.get('full_name','').casefold()!=repository.casefold():
        raise ValueError('Only explicitly identified public repositories are supported')
    actual_commit=api(f'repos/{repository}/commits/{commit}')
    run=api(f'repos/{repository}/actions/runs/{run_id}')
    check=api(f'repos/{repository}/check-runs/{check_id}')
    mismatches=[]
    if actual_commit.get('sha')!=commit:mismatches.append('commit_identity')
    for label,doc in [('run',run),('check',check)]:
        if doc.get('head_sha')!=commit:mismatches.append(label+'_head_sha')
        if doc.get('status')!='completed' or doc.get('conclusion')!='success':mismatches.append(label+'_not_success')
    if str(run.get('id'))!=str(run_id) or str(check.get('id'))!=str(check_id):mismatches.append('requested_ids')
    suite=check.get('check_suite',{}).get('id')
    if suite is None or run.get('check_suite_id')!=suite:mismatches.append('check_suite_identity')
    if run.get('repository',{}).get('full_name','').casefold()!=repository.casefold():mismatches.append('run_repository')
    if check.get('app',{}).get('slug')!='github-actions':mismatches.append('check_app')
    return {'schema':'github-check-observation-v1','observed_at':dt.datetime.now(dt.timezone.utc).isoformat(),
        'repository':repository,'requested_commit':commit,'run_id':str(run_id),'check_id':str(check_id),
        'identity_and_success_verified':not mismatches,'mismatches':mismatches,
        'run':{k:run.get(k) for k in ('id','head_sha','status','conclusion','event','path','run_attempt','html_url','check_suite_id')},
        'check':{k:check.get(k) for k in ('id','name','head_sha','status','conclusion','details_url','started_at','completed_at')},
        'raw_response_sha256':hashlib.sha256(json.dumps({'repository':repo,'commit':actual_commit,'run':run,'check':check},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),
        'assurance':'GitHub metadata only; no artifact replay, workflow trust, scope or engineering acceptance inferred',
        'scope_verified':False,'oracle_replayed':False,'inbox_eligible':False,'canonical_eligible':False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository',required=True);p.add_argument('--commit',required=True)
    p.add_argument('--run-id',required=True);p.add_argument('--check-id',required=True)
    a=p.parse_args();gh=shutil.which('gh')
    if not gh:raise SystemExit('GitHub CLI is required; authenticate outside this script.')
    def api(endpoint):
        r=subprocess.run([gh,'api',endpoint],capture_output=True,text=True,encoding='utf-8',timeout=45)
        if r.returncode:raise ValueError('GitHub API lookup failed for '+endpoint)
        return json.loads(r.stdout)
    try:
        r=collect(a.repository,a.commit,a.run_id,a.check_id,api)
        print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['identity_and_success_verified'] else 2
    except (ValueError,KeyError,TypeError,subprocess.TimeoutExpired) as e:
        print(json.dumps({'status':'not_verified','reason':str(e),'inbox_eligible':False}));return 2

if __name__=='__main__':raise SystemExit(main())
