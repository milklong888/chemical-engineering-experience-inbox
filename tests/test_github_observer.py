import copy, importlib.util, pathlib, unittest
p=pathlib.Path(__file__).resolve().parents[1]/'scripts/observe_github_check.py'
s=importlib.util.spec_from_file_location('observer',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

class GitHubObservationTests(unittest.TestCase):
    def setUp(self):
        self.sha='a'*40;self.repo='owner/methods'
        self.docs={f'repos/{self.repo}':{'full_name':self.repo,'private':False},
          f'repos/{self.repo}/commits/{self.sha}':{'sha':self.sha},
          f'repos/{self.repo}/actions/runs/12':{'id':12,'head_sha':self.sha,'status':'completed','conclusion':'success','check_suite_id':8,'repository':{'full_name':self.repo}},
          f'repos/{self.repo}/check-runs/34':{'id':34,'head_sha':self.sha,'status':'completed','conclusion':'success','check_suite':{'id':8},'app':{'slug':'github-actions'}}}
    def run_check(self):return m.collect(self.repo,self.sha,'12','34',lambda k:copy.deepcopy(self.docs[k]))
    def test_exact_identity_is_metadata_only(self):
        r=self.run_check();self.assertTrue(r['identity_and_success_verified']);self.assertFalse(r['inbox_eligible']);self.assertFalse(r['scope_verified'])
    def test_old_green_commit(self):
        self.docs[f'repos/{self.repo}/check-runs/34']['head_sha']='b'*40
        self.assertIn('check_head_sha',self.run_check()['mismatches'])
    def test_cancelled_run(self):
        self.docs[f'repos/{self.repo}/actions/runs/12']['conclusion']='cancelled'
        self.assertFalse(self.run_check()['identity_and_success_verified'])
    def test_unrelated_suite(self):
        self.docs[f'repos/{self.repo}/check-runs/34']['check_suite']['id']=99
        self.assertIn('check_suite_identity',self.run_check()['mismatches'])
    def test_custom_badge_app(self):
        self.docs[f'repos/{self.repo}/check-runs/34']['app']['slug']='custom-badge'
        self.assertIn('check_app',self.run_check()['mismatches'])
    def test_wrong_repository(self):
        self.docs[f'repos/{self.repo}/actions/runs/12']['repository']['full_name']='other/project'
        self.assertIn('run_repository',self.run_check()['mismatches'])
    def test_private_repository_not_exported(self):
        self.docs[f'repos/{self.repo}']['private']=True
        with self.assertRaises(ValueError):self.run_check()
    def test_ref_injection_rejected_before_network(self):
        with self.assertRaises(ValueError):m.collect('owner/repo','main?all=true','12','34',lambda k:self.fail('network'))
    def test_missing_app_or_suite(self):
        del self.docs[f'repos/{self.repo}/check-runs/34']['check_suite']
        self.assertFalse(self.run_check()['identity_and_success_verified'])

if __name__=='__main__':unittest.main()
